"""Genera mundos sintéticos independientes de un único motor y sus apoyos.
No remuestrea la v2. Todos los parámetros mecánicos son supuestos didácticos.
Ejecutar en Spyder sin argumentos o consola: --config RUTA --out CARPETA.
"""
import argparse
from pathlib import Path
import shutil
import numpy as np
import pandas as pd
from comun import ROOT, ASSEMBLY, MOTOR, DE, NDE, SIGNALS, config, write, dump, sha, empty_events

from fisica import schedule_physics, configurations, sensor_contract, PHYSICS_SIGNALS

def simulate(c, number, products):
    run = f'R{number:02d}'
    stress = number > c['base_runs']
    spec = c['run_specs'][number-1]
    variant = 1 if spec['scenario']=='stress_carga' else 2 if spec['scenario']=='stress_mecanismo_ruido' else 0
    seeds = np.random.SeedSequence([spec['seed'], number]).spawn(5)
    rp, rm, rs, ra, rf = [np.random.default_rng(s) for s in seeds]
    step = c['step_minutes']; dt = step/60
    times = pd.date_range(c['start'], periods=c['days']*24*60//step, freq=f'{step}min')
    n = len(times); at = lambda k: times[0]+pd.Timedelta(minutes=int(k)*step)
    # Product/cycle schedule is independent of subsequent machine failures.
    regime = np.full(n, 'parado', dtype=object)
    grade = np.full(n, None, dtype=object); recipe_block = grade.copy()
    th = np.full(n, np.nan); wid = th.copy(); factor = np.ones(n)
    planned_load = np.zeros(n); speed_plan = np.zeros(n)
    recipe_counter = 0
    shifts=[]; cursor=0
    while cursor<n:
        length=int(rp.integers(c['schedule']['shift_slots_min'],c['schedule']['shift_slots_max']+1))
        shifts.append((cursor,min(cursor+length,n))); cursor+=length
    for start,shift_end in shifts:
        operating_end=max(start+4,shift_end-int(rp.integers(c['schedule']['off_slots_min'],c['schedule']['off_slots_max']+1)))
        operating_end=min(operating_end,n)
        regime[start:min(start+2,n)] = 'arranque'
        regime[start+2:min(start+4,n)] = 'sin_carga'
        regime[start+4:operating_end] = 'laminacion'
        regime[operating_end:min(operating_end+2,n)] = 'desaceleracion'
        k = start+4
        while k < operating_end:
            e = min(k+int(rp.integers(4, 13)), operating_end)
            gi = int(rp.choice(len(products), p=[.35,.30,.25,.10] if variant!=1 else [.10,.20,.35,.35]))
            product = products.iloc[gi]
            choices = np.array([1,1.2,1.5,2,2.5,3,4,6,8,10,12,15])
            choices = choices[choices >= product.espesor_min_demo_mm]
            t = float(rp.choice(choices)); w = float(rp.choice([1000,1100,1250,1400,1500,1550]))
            recipe_counter += 1
            grade[k:e] = product.grado_acero; recipe_block[k:e] = f'{run}-C{recipe_counter:06d}'
            th[k:e] = t; wid[k:e] = w; factor[k:e] = product.factor_carga_demo
            k=e
    physical_plan,speed_plan,planned_load,eff_plan,domain = schedule_physics(c,times,regime,th,wid,factor,rf,variant)
    physical_clean=physical_plan.copy()
    clean_rpm=np.zeros(n);clean_current=np.zeros(n);clean_load=np.zeros(n);clean_eff=np.zeros(n)
    # Latent state and multi-signal noise; distinct RNG streams preserve causality.
    d = rm.uniform(.03,.14,3)
    life = np.array(c['life_hours_median'])*spec['life_factor']*rm.lognormal(0,.22,3)
    gain = rm.lognormal(0,.24,(3,3))
    thermal = np.array([32.,31.,37.]); noise=np.zeros(8)
    latent=np.zeros((n,3)); measured=np.zeros((n,len(SIGNALS)))
    history=np.zeros(n); last_type=np.full(n,'sin_historial',dtype=object)
    cumhours=0.; last_service_hours=0.; service_type='sin_historial'
    operating=np.zeros(n,bool); fault_mask=np.zeros(n,bool)
    lubrication=np.zeros(n); cooling=np.zeros(n)
    # Exogenous context disturbances, not all produce failures.
    for arr in [lubrication,cooling]:
        for _ in range(max(1,int(c['days']/9))):
            s=int(rp.integers(0,max(1,n-288))); e=min(n,s+int(rp.integers(36,288)))
            arr[s:e]=rp.uniform(.25,.85)
    faults=[]; maint=[]; repairs=[]
    due_dates=[];cursor=0
    while cursor<n:
        cursor+=int((spec['pm_interval_days']+rp.integers(-c['schedule']['pm_jitter_days'],c['schedule']['pm_jitter_days']+1))*24*60//step)
        if cursor<n:due_dates.append(cursor)
    plans=[];pm_index=0;delayed=False
    for j,due in enumerate(due_dates):
        plans.append(dict(run_id=run,plan_id=f'{run}-P{j+1:04d}',revision=1,
            known_at=at(max(0,due-c['schedule']['notice_days']*24*60//step)),scheduled_start=at(due),status='previsto',planned_duration_hours=c['pm_duration_hours']))
    next_pm=due_dates[0] if due_dates else n+1; block_end=-1; pending=None
    for k in range(n):
        if k==block_end and pending is not None:
            typ, component, maintenance_id = pending
            before=d.copy()
            if typ=='preventivo':
                d*=rm.uniform(spec['restore_min'],spec['restore_max'],3)
                treatment='mejora_parcial'
            elif rm.random()<.65:
                d[component]=min(d[component],rm.uniform(.015,.10))
                life[component]=c['life_hours_median'][component]*spec['life_factor']*rm.lognormal(0,.22)
                gain[component]=rm.lognormal(0,.24,3)
                treatment='sustitucion'
            else:
                d[component]*=rm.uniform(.35,.70)
                treatment='reparacion_parcial'
            for j,aid in enumerate([DE,NDE,MOTOR]):
                if typ=='preventivo' or j==component:
                    repairs.append(dict(run_id=run,maintenance_id=maintenance_id,asset_id=aid,
                        damage_before=before[j],damage_after=d[j],action=treatment))
            maint[-1]['action']=treatment
            # Completion is reported with 15 min lag; history updates only then.
            maint[-1]['completed_operating_hours']=cumhours
            pending=None
        if k==next_pm and k<block_end:
            delayed=True
            plans.append(dict(run_id=run,plan_id=f'{run}-P{pm_index+1:04d}',revision=2,known_at=at(k),scheduled_start=pd.NaT,status='aplazado_correctivo',planned_duration_hours=c['pm_duration_hours']))
        if k>=block_end and k>=next_pm:
            end=min(n,k+round(c['pm_duration_hours']/dt))
            mid=f'{run}-M{len(maint)+1:04d}'
            maint.append(dict(run_id=run,maintenance_id=mid,assembly_id=ASSEMBLY,asset_id=ASSEMBLY,
                start=at(k),end=at(end),kind='preventivo',event_id=None,
                known_at=at(k),result_available_at=at(end)+pd.Timedelta(minutes=15),
                action='pendiente',completed_operating_hours=np.nan))
            plans.append(dict(run_id=run,plan_id=f'{run}-P{pm_index+1:04d}',revision=3 if delayed else 2,known_at=at(k),scheduled_start=at(k),status='iniciado',planned_duration_hours=c['pm_duration_hours']))
            block_end=end; pending=('preventivo',None,mid); pm_index+=1; delayed=False
            next_pm=due_dates[pm_index] if pm_index<len(due_dates) else n+1
        state=regime[k]
        if k<block_end:
            state='mantenimiento' if pending[0]=='preventivo' else 'fallo'
        load=planned_load[k] if state not in ['parado','fallo','mantenimiento'] else 0.
        rpm=speed_plan[k] if load>0 else 0.
        active=load>0
        # Stochastic competing hazards: no observable threshold forces failure.
        if active and k>0 and operating[k-1]:
            severity=np.maximum(d-.35,0)
            if variant==2:
                rates=c['failure_rate_per_hour']*(severity**2.2)*(1+.6*cooling[k])
            else:
                rates=c['failure_rate_per_hour']*(severity**3)
            rates*=max(load,.15)**.5
            sudden=rm.random() < -np.expm1(-dt*c['sudden_rate_per_hour'])
            progressive=rm.random() < -np.expm1(-dt*rates.sum())
            if sudden or progressive:
                comp=2 if sudden else int(rm.choice(3,p=rates/rates.sum()))
                end=min(n,k+max(2,int(np.ceil(rm.lognormal(np.log(4),.5)/dt))))
                eid=f'{run}-E{len(faults)+1:04d}'; mid=f'{run}-M{len(maint)+1:04d}'
                mode='electrico_subito' if sudden else ['rodamiento_de','rodamiento_nde','termico_motor'][comp]
                faults.append(dict(run_id=run,event_id=eid,assembly_id=ASSEMBLY,asset_id=[DE,NDE,MOTOR][comp],
                    start=at(k),end=at(end),mode=mode,onset='subito' if sudden else 'progresivo',
                    detected_at=at(k),diagnosis_available_at=at(end)+pd.Timedelta(minutes=15)))
                maint.append(dict(run_id=run,maintenance_id=mid,assembly_id=ASSEMBLY,asset_id=[DE,NDE,MOTOR][comp],
                    start=at(k),end=at(end),kind='correctivo',event_id=eid,known_at=at(k),
                    result_available_at=at(end)+pd.Timedelta(minutes=15),action='pendiente',completed_operating_hours=np.nan))
                block_end=end;pending=('correctivo',comp,mid)
                state='fallo';load=0.;rpm=0.;active=False
        regime[k]=state
        if state!='laminacion':
            grade[k]=None;recipe_block[k]=None;th[k]=np.nan;wid[k]=np.nan
        operating[k]=active;fault_mask[k]=state=='fallo'
        # Record only completed maintenance knowledge; no future closeout joins.
        for m in reversed(maint):
            if m['result_available_at']<=at(k) and np.isfinite(m['completed_operating_hours']):
                last_service_hours=m['completed_operating_hours'];service_type=m['kind'];break
        history[k]=cumhours-last_service_hours;last_type[k]=service_type
        ambient=19+5*np.sin(2*np.pi*k*dt/(365*24))+2*np.sin(2*np.pi*k*dt/24)
        noise=.8*noise+rs.normal(0,.6,8)*(1.7 if variant==2 else 1)
        # Thermal inertia retained in all operating states, including shutdown.
        pre=np.maximum(d-.25,0)**(1.25 if variant!=2 else .8)
        hot=np.array([ambient+active*(19+28*load+gain[0,0]*14*pre[0]+12*lubrication[k]),
                      ambient+active*(18+26*load+gain[1,0]*14*pre[1]+10*lubrication[k]),
                      ambient+active*(25+49*load+gain[2,0]*18*pre[2]+18*cooling[k])])
        thermal+=(hot-thermal)*(1-np.exp(-dt/np.array([.7,.8,1.3])))
        vb=.20+active*(.7+.9*load+.0006*rpm)
        vde=max(.03,vb+active*(gain[0,1]*2.5*pre[0]+.20*pre[1])+.12*noise[0])
        vnde=max(.03,vb+active*(gain[1,1]*2.4*pre[1]+.20*pre[0])+.12*noise[1])
        # Motor efficiency degrades smoothly; no deterministic failure threshold.
        efficiency=eff_plan[k]*(1-.05*min(pre[2],3.))
        physical_clean[k]=physical_plan[k] if active else 0.
        if state!='laminacion':
            for col in ['entry_thickness_mm','exit_thickness_mm','strip_temperature_c']:
                physical_clean[k,list(PHYSICS_SIGNALS).index(col)]=np.nan
        mechanical=physical_clean[k,list(PHYSICS_SIGNALS).index('mechanical_power_kw')]
        electrical=mechanical/efficiency
        physical_clean[k,list(PHYSICS_SIGNALS).index('electrical_power_kw')]=electrical
        current=electrical*1000/(np.sqrt(3)*c['physics']['voltage_ll_v']*c['physics']['power_factor'])
        clean_rpm[k]=rpm;clean_current[k]=current;clean_load[k]=load;clean_eff[k]=efficiency
        measured[k,15:]=physical_clean[k]
        measured[k,:15]=[thermal[0]+.6*noise[0],thermal[1]+.6*noise[1],thermal[2]+noise[2],vde,vnde,
            max(.01,active*(.6+.003*rpm+gain[0,2]*3*pre[0])+.10*noise[3]),
            max(.01,active*(.6+.003*rpm+gain[1,2]*3*pre[1])+.10*noise[4]),
            max(1.1,3+active*3*pre[0]+.25*noise[5]),max(1.1,3+active*3*pre[1]+.25*noise[6]),
            current,max(0,load+.012*noise[2]) if active else 0.,max(0,rpm+4*noise[7]) if active else 0.,
            ambient+.15*noise[6],max(0,active*(90+60*load)*(1-.65*cooling[k])+noise[5]),
            max(0,active*4.5*(1-.55*lubrication[k])+.05*noise[4])]
        latent[k]=d
        # Damage affects future intervals. Imperfect restoration and shocks remain latent.
        if active:
            stress_load=(max(load,.12)/.6)**(2.0 if variant!=2 else 2.5)
            d+=dt/life*stress_load*np.array([1+lubrication[k],1+.8*lubrication[k],1+cooling[k]])*rm.lognormal(0,.12,3)
            if rm.random()<dt/110:
                d[int(rm.integers(0,3))]+=rm.uniform(.01,.08)
            cumhours+=dt
    # Physically coherent reference remains private; never a model input.
    physics_truth=pd.DataFrame(physical_clean,columns=PHYSICS_SIGNALS)
    physics_truth['run_id']=run;physics_truth['assembly_id']=ASSEMBLY;physics_truth['timestamp']=times
    physics_truth['motor_speed_rpm']=clean_rpm;physics_truth['current_a']=clean_current
    physics_truth['load_ratio']=clean_load;physics_truth['motor_efficiency_effective']=clean_eff
    physics_truth['width_mm']=wid
    # Independent sensor defects injected AFTER physical simulation.
    measured*=np.where(domain,c['physics']['sensor_gain_after'],1.)[:,None]
    incidents=[]
    measured*=ra.normal(1,c['sensor_defects']['gain_std'],len(SIGNALS))
    measured[:,:3]+=ra.normal(0,c['sensor_defects']['temp_bias_sd'],3)
    def record(col,s,e,kind):
        incidents.append(dict(run_id=run,incident_id=f'{run}-S{len(incidents)+1:04d}',sensor_id='S-'+col,start=at(s),end=at(e),kind=kind))
    for j,col in enumerate(SIGNALS):
        measured[ra.random(n)<(.004 if not stress else .009),j]=np.nan
        lo,hi=SIGNALS[col][1:3]
        for kind in ['sin_datos','congelado','pico','deriva']:
            for _ in range(ra.poisson(c['sensor_defects']['blocks_poisson_mean_per_kind'])):
                s=int(ra.integers(48,max(49,n-96)));e=min(n,s+int(ra.integers(6,73)))
                if kind=='sin_datos':measured[s:e,j]=np.nan
                elif kind=='congelado':measured[s:e,j]=measured[s-1,j]
                elif kind=='pico':
                    slots=np.arange(s,e)[ra.random(e-s)<.3]
                    vals=measured[slots,j]+ra.uniform(.05,.3,len(slots))*(hi-lo)
                    measured[slots,j]=np.where(ra.random(len(slots))<.5,hi*ra.uniform(1.02,1.4,len(slots)),np.clip(vals,lo,hi*.98))
                else:measured[s:e,j]=np.clip(measured[s:e,j]+np.linspace(0,ra.uniform(-.2,.2)*(hi-lo),e-s),lo,hi*.98)
                record(col,s,e,kind)
    for _ in range(ra.poisson(c['sensor_defects']['correlated_outage_mean'])):
        s=int(ra.integers(48,n-24));e=s+int(ra.integers(3,19));measured[s:e,:]=np.nan
        for col in SIGNALS:record(col,s,e,'sin_datos_correlacionada')
    delay=ra.choice([0,5,10,20],size=n,p=[.94,.035,.02,.005] if not stress else [.88,.06,.04,.02])
    frame=pd.DataFrame(measured,columns=SIGNALS)
    frame.insert(0,'timestamp',times);frame.insert(0,'assembly_id',ASSEMBLY);frame.insert(0,'run_id',run)
    frame['available_at']=times+pd.to_timedelta(delay,unit='min')
    frame['stand_id']=c['physics']['stand_id']
    frame['configuration_id']=np.where(domain,'CFG-02','CFG-01')
    frame['rolling_state']=regime;frame['production_segment_id']=pd.array(recipe_block,dtype='string')
    frame['steel_family']=pd.array(grade,dtype='string');frame['target_thickness_mm']=th;frame['width_mm']=wid
    frame['run_hours_since_service']=history;frame['known_service_type']=last_type
    active_series=pd.Series(operating)
    frame['starts_last_24h']=(active_series&~active_series.shift(1,fill_value=False)).rolling(288,min_periods=1).sum().astype('int16')
    # Identifiers denote contiguous recipe/operation blocks, never physical coils.
    context=['rolling_state','production_segment_id','configuration_id']
    changed=frame[context].fillna('__null__').astype(str).ne(frame[context].fillna('__null__').astype(str).shift()).any(axis=1)
    frame['production_segment_id']=[f'{run}-SEG{j:06d}' for j in changed.cumsum()]
    truth=frame[['run_id','assembly_id','timestamp']].copy()
    truth[['damage_de','damage_nde','damage_motor']]=latent
    truth['health_state']=np.where(fault_mask,'fallo',np.where(latent.max(axis=1)>=.55,'degradacion','normal'))
    # Complete latent episodes, used only for conservative boundary exclusions.
    episodes=[]
    for j,aid in enumerate([DE,NDE,MOTOR]):
        mask=latent[:,j]>=.55
        starts=np.flatnonzero(mask&~np.r_[False,mask[:-1]])
        ends=np.flatnonzero(mask&~np.r_[mask[1:],False])+1
        for s,e in zip(starts,ends):
            episodes.append(dict(run_id=run,episode_id=f'{run}-D{len(episodes)+1:04d}',asset_id=aid,start=at(s),end=at(e)))
    fault_cols=['run_id','event_id','assembly_id','asset_id','start','end','mode','onset','detected_at','diagnosis_available_at']
    maint_cols=['run_id','maintenance_id','assembly_id','asset_id','start','end','kind','event_id','known_at','result_available_at','action','completed_operating_hours']
    faults=empty_events(faults,fault_cols,['start','end','detected_at','diagnosis_available_at'])
    maintenance=empty_events(maint,maint_cols,['start','end','known_at','result_available_at'])
    episodes=empty_events(episodes,['run_id','episode_id','asset_id','start','end'],['start','end'])
    incidents=empty_events(incidents,['run_id','incident_id','sensor_id','start','end','kind'],['start','end'])
    repairs=pd.DataFrame(repairs,columns=['run_id','maintenance_id','asset_id','damage_before','damage_after','action'])
    plans=empty_events(plans,['run_id','plan_id','revision','known_at','scheduled_start','status','planned_duration_hours'],['known_at','scheduled_start'])
    return frame,truth,faults,maintenance,episodes,incidents,repairs,plans,physics_truth

def main(config_path=None,out=None):
    c=config(config_path);root=Path(out or ROOT);root.mkdir(parents=True,exist_ok=True)
    if (root/'data/telemetria').exists():
        raise FileExistsError('El destino ya contiene telemetría. Usa --out con una carpeta nueva para preservar versiones.')
    dump(c,root/'config/escenario.json')
    products=pd.read_parquet(ROOT/'config/productos_base_v2.parquet')
    write(products,root/'data/productos.parquet')
    assets=pd.DataFrame([
        ('DEMO-ACB',None,'planta','Contexto ACB sintético'),
        ('DEMO-LAM','DEMO-ACB','linea','Tren lógico'),
        ('DEMO-C01','DEMO-LAM','caja','Caja representativa sin equivalencia real'),
        (ASSEMBLY,'DEMO-C01','conjunto','Motor y apoyos'),
        (MOTOR,ASSEMBLY,'motor','Motor lógico'),(DE,MOTOR,'apoyo','Lado accionamiento'),(NDE,MOTOR,'apoyo','Lado opuesto')],
        columns=['asset_id','parent_asset_id','asset_type','description'])
    assets['is_synthetic']=True
    write(assets,root/'data/activos.parquet')
    sensors=sensor_contract(SIGNALS)
    write(configurations(c),root/'data/configuraciones.parquet')
    write(sensors,root/'data/sensores.parquet')
    totals=[];tables={k:[] for k in ['fallos','mantenimiento','episodios','incidencias_sensores','reparaciones','plan_mantenimiento']}
    runs=[]
    for i in range(1,c['runs']+1):
        frame,truth,fault,maint,episodes,incidents,repairs,plans,physics_truth=simulate(c,i,products)
        run=f'R{i:02d}';write(physics_truth,root/f'sim_truth/fisica/{run}.parquet');write(frame,root/f'data/telemetria/{run}.parquet');write(truth,root/f'sim_truth/estado_latente/{run}.parquet')
        for name,df in zip(tables,[fault,maint,episodes,incidents,repairs,plans]):tables[name].append(df)
        end=pd.Timestamp(c['start'])+pd.Timedelta(days=c['days'])
        runs.append(dict(run_id=run,assembly_id=ASSEMBLY,seed=c['run_specs'][i-1]['seed'],subseed_index=i,version=c['version'],
            start=pd.Timestamp(c['start']),end=end,scenario=c['run_specs'][i-1]['scenario'],
            step_minutes=c['step_minutes'],decision_minutes=c['decision_minutes'],config_sha256=sha(root/'config/escenario.json')))
        totals.append(dict(run_id=run,telemetry_rows=len(frame),failures=len(fault),maintenance=len(maint),
            sudden_failures=int(fault.onset.eq('subito').sum()),operating_hours=float(frame.rolling_state.isin(['arranque','sin_carga','laminacion','desaceleracion']).sum()*5/60)))
        print(run,'telemetría',len(frame),'fallos',len(fault),flush=True)
    for name,frames in tables.items():
        folder='data' if name in ['fallos','mantenimiento','plan_mantenimiento'] else 'sim_truth'
        write(pd.concat(frames,ignore_index=True),root/f'{folder}/{name}.parquet')
    write(pd.DataFrame(runs),root/'data/ejecuciones.parquet')
    dump({'version':c['version'],'runs':totals,'telemetry_rows':sum(x['telemetry_rows'] for x in totals),
          'failure_count':sum(x['failures'] for x in totals),'models_trained':False},root/'resultados/generacion.json')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config');p.add_argument('--out');a=p.parse_args();main(a.config,a.out)
