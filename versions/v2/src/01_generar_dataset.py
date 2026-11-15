"""Simulación cronológica reproducible. Ejecutable desde Spyder o consola.
Todas las distribuciones y ecuaciones son HIPÓTESIS didácticas, no parámetros ACB.
"""
from pathlib import Path
import argparse
import json
import sys
import numpy as np
import pandas as pd
from scipy.signal import lfilter

ROOT = Path(__file__).resolve().parents[1]
MODES = ['rodamiento', 'reductor', 'lubricacion', 'hidraulico', 'refrigeracion', 'electrico_subito']

def write(df, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    for c in df.select_dtypes(include='float64').columns:
        df[c] = df[c].astype('float32')
    df.to_parquet(path, index=False, compression='zstd')

def main(config_path=None, out=None):
    cfg = json.loads(Path(config_path or ROOT/'config/escenario.json').read_text())
    root = Path(out or ROOT)
    for folder in ['data/telemetria','ml/features','ml/targets','privado_no_usar_como_features','resultados']:
        (root/folder).mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(cfg['seed'])
    times = pd.date_range(cfg['start'], cfg['end_exclusive'], freq=f"{cfg['step_minutes']}min", inclusive='left')
    n, dt = len(times), cfg['step_minutes']/60
    step, end = cfg['step_minutes'], pd.Timestamp(cfg['end_exclusive'])
    def at(k): return times[0] + pd.Timedelta(minutes=int(k)*step)
    asset_rows = []
    def add(code, kind, pos, nominal_kw, modes):
        asset_rows.append(dict(equipo_id=code, tipo_equipo=kind, posicion=pos,
            potencia_nominal_kw=nominal_kw, modos_admisibles='|'.join(MODES[i] for i in modes),
            origen='sintetico', inventario_real=False))
    add('CC_A','colada',0,180,[0,1,4,5]); add('CC_B','colada',0,180,[0,1,4,5])
    add('HT_A','horno_tunel',1,240,[0,1,4,5]); add('HT_B','horno_tunel',1,240,[0,1,4,5])
    add('DESC','descascarillador',2,500,[0,4,5]); add('CIZ','cizalla',3,350,[0,1,3,5])
    for j in range(7): add(f'F{j+1}','caja_laminacion',j+4,3500 if j<3 else 2500,[0,1,2,3,4,5])
    add('ENF','enfriamiento',11,400,[0,4,5])
    add('BOB_A','bobinadora',12,700,[0,1,3,5]); add('BOB_B','bobinadora',12,700,[0,1,3,5])
    add('HID','central_hidraulica',4,350,[0,3,5]); add('LUB','central_lubricacion',4,150,[0,2,5])
    assets=pd.DataFrame(asset_rows); m=len(assets)
    write(assets,root/'data/equipos.parquet')
    # Four limited product families. No claim of complete present commercial catalogue.
    products=pd.DataFrame([
        ('DD11',1.0,1.00),('S235JR',1.5,1.08),('S355JR',2.0,1.22),('S500MC',2.0,1.40)],
        columns=['grado_acero','espesor_min_demo_mm','factor_carga_demo'])
    write(products,root/'data/productos.parquet')
    # Product recipe is chosen at campaign start, independent of future faults.
    thicknesses=np.array([1,1.2,1.5,2,2.5,3,4,6,8,10,12,15],float)
    recipe=np.empty((n,4),dtype=np.float32)
    campaign_steps=int(8/dt)
    for s in range(0,n,campaign_steps):
        gi=int(rng.choice(4,p=[.35,.3,.25,.1]))
        options=thicknesses[thicknesses>=products.iloc[gi].espesor_min_demo_mm]
        # Exogenous product mix shift after 12 months, not a sensor label.
        weights=np.linspace(1.6,.6,len(options)) if at(s)<pd.Timestamp(cfg['train_end']) else np.linspace(.8,1.2,len(options))
        thick=float(rng.choice(options,p=weights/weights.sum()))
        recipe[s:s+campaign_steps]=[gi,thick,rng.choice([1000,1100,1250,1400,1500,1550]),products.iloc[gi].factor_carga_demo]
    allowed=[[MODES.index(x) for x in row.modos_admisibles.split('|') if x!='electrico_subito'] for row in assets.itertuples()]
    mode=np.array([rng.choice(x) for x in allowed])
    damage=rng.uniform(.04,.35,m)
    # Different duty and load accumulate different damage. Lognormal cycle life.
    life=rng.lognormal(np.log(450),.40,m)
    dmg=np.zeros((n,m),np.float32); mod=np.zeros((n,m),np.int8)
    active=np.zeros((n,m),bool); status=np.zeros((n,m),np.int8)
    age=np.zeros((n,m),np.float32); loads=np.zeros((n,m),np.float32)
    maintained=np.zeros(m); operation_age=np.zeros(m)
    coil_id=np.zeros(n,np.int32); grade=np.zeros(n,np.int8)
    thick=np.zeros(n,np.float32); width=np.zeros(n,np.float32); speed=np.zeros(n,np.float32)
    massflow=np.zeros(n,np.float32); line_state=np.zeros(n,np.int8)
    entrytemp=np.zeros(n,np.float32)
    failures=[]; maint=[]; outages=[]; coils=[]
    pm_interval=int(cfg['planned_interval_days']*24/dt); pm_len=int(cfg['planned_duration_hours']/dt)
    pm_starts=list(range(pm_interval,n,pm_interval))
    pm_mask=np.zeros(n,bool)
    for s in pm_starts:
        e=min(s+pm_len,n); pm_mask[s:e]=True
        outages.append(dict(parada_id=f'P{len(outages)+1:05d}',inicio=at(s),fin=at(e),tipo='programada',evento_id=None,equipo_causa=None))
        for a in range(m):
            maint.append(dict(mantenimiento_id=f'M{len(maint)+1:06d}',equipo_id=assets.iloc[a].equipo_id,
                inicio=at(s),fin=at(e),tipo='preventivo',evento_id=None,conocido_desde=at(max(0,s-int(7*24/dt))),
                coste_eur_simulado=float(rng.uniform(250,1100))))
    blocked_until=0; failed_asset=-1; current=None; current_remaining=0
    def finish_coil(k, complete):
        nonlocal current
        if current is None:return
        current['fin']=at(k)
        current['estado_resultado']='completa' if complete else 'interrumpida'
        current['masa_procesada_t']=current['masa_objetivo_t']*(current['pasos_procesados']/current['pasos_objetivo'])
        # Future quality outcome: never used as ML feature.
        current['espesor_medido_final_mm']=current['espesor_objetivo_mm']*(1+rng.normal(0,.006))
        current['disponible_resultado_desde']=at(k)+pd.Timedelta(minutes=10)
        coils.append(current);current=None
    for k in range(n):
        if k in pm_starts:
            finish_coil(k,False)
            damage*=.45
            maintained[:]=k
        if k==blocked_until and failed_asset>=0:
            a=failed_asset;damage[a]=rng.uniform(.01,.07);life[a]=rng.lognormal(np.log(450),.40)
            mode[a]=rng.choice(allowed[a]);maintained[a]=k;failed_asset=-1
        in_pm=pm_mask[k]
        outage=k<blocked_until
        # A fault appears after the previous interval's stress, only for an operating unit.
        if not outage and not in_pm and k>0:
            candidates=np.flatnonzero((damage>=1)&active[k-1])
            sudden=np.flatnonzero(active[k-1] & (rng.random(m)<dt/18000))
            a=int(candidates[np.argmax(damage[candidates])]) if len(candidates) else (int(sudden[0]) if len(sudden) else -1)
            if a>=0:
                is_sudden=not len(candidates)
                fm=5 if is_sudden else int(mode[a])
                duration=max(2,int(np.ceil(rng.lognormal(np.log(3.0),.50)/dt)))
                blocked_until=min(k+duration,n); failed_asset=a;outage=True
                eid=f'E{len(failures)+1:05d}';aid=assets.iloc[a].equipo_id
                failures.append(dict(evento_id=eid,equipo_id=aid,inicio=at(k),fin=at(blocked_until),
                    modo_fallo=MODES[fm],tipo_inicio='subito' if is_sudden else 'progresivo',
                    diagnostico_disponible_desde=at(blocked_until),duracion_h=(blocked_until-k)*dt,
                    coste_reparacion_eur_simulado=float(rng.uniform(800,12000))))
                maint.append(dict(mantenimiento_id=f'M{len(maint)+1:06d}',equipo_id=aid,inicio=at(k),fin=at(blocked_until),
                    tipo='correctivo',evento_id=eid,conocido_desde=at(k),coste_eur_simulado=failures[-1]['coste_reparacion_eur_simulado']))
                outages.append(dict(parada_id=f'P{len(outages)+1:05d}',inicio=at(k),fin=at(blocked_until),
                    tipo='no_programada',evento_id=eid,equipo_causa=aid))
                finish_coil(k,False)
        line_state[k]=1 if in_pm else (2 if outage else 0)
        dmg[k]=damage;mod[k]=mode;age[k]=(k-maintained)*dt
        if in_pm or outage:
            status[k]=1 if in_pm else 2
            if failed_asset>=0:status[k,failed_asset]=3
            continue
        if current is None:
            gi,th,wid,fac=recipe[k];gi=int(gi)
            weight=min(28,float(rng.uniform(10,18)*wid/1000))
            length=weight*1000/(7850*(wid/1000)*(th/1000))
            target_flow=rng.uniform(36,48) # kg/s hypothetical, not measured plant throughput
            duration_steps=max(1,int(np.ceil(weight*1000/target_flow/(step*60))))
            cid=len(coils)+1
            current=dict(bobina_id=cid,inicio=at(k),grado_acero=products.iloc[gi].grado_acero,
                espesor_objetivo_mm=float(th),ancho_mm=float(wid),masa_objetivo_t=weight,
                longitud_objetivo_m=length,pasos_objetivo=duration_steps,pasos_procesados=0,
                rama_colada='A' if cid%2 else 'B',bobinadora_id='BOB_A' if cid%2 else 'BOB_B')
            current_remaining=duration_steps
        c=current;gi=products.index[products.grado_acero==c['grado_acero']][0]
        th,wid=c['espesor_objetivo_mm'],c['ancho_mm']
        coil_id[k]=c['bobina_id'];grade[k]=gi;thick[k]=th;width[k]=wid
        speed[k]=c['longitud_objetivo_m']/(c['pasos_objetivo']*step*60)
        massflow[k]=7850*wid/1000*th/1000*speed[k]
        entrytemp[k]=1170+rng.normal(0,8)
        act=np.ones(m,bool)
        if c['rama_colada']=='A':act[[1,3,15]]=False
        else:act[[0,2,14]]=False
        active[k]=act;status[k]=np.where(act,0,4)
        factor=float(products.iloc[gi].factor_carga_demo)
        load=np.clip(.45+.15*np.log(60/th)/np.log(60)+.16*(factor-1)+.13*(wid/1250-1)+rng.normal(0,.035,m),.15,1.2)
        loads[k]=load*act
        operation_age+=act*dt
        damage+=act*(dt/life)*(load/.60)**1.8*rng.lognormal(0,.10,m)
        current['pasos_procesados']+=1;current_remaining-=1
        if current_remaining==0:finish_coil(k+1,True)
    finish_coil(n,False)
    failures=pd.DataFrame(failures);maint=pd.DataFrame(maint).sort_values(['inicio','equipo_id']).reset_index(drop=True)
    outages=pd.DataFrame(outages).sort_values('inicio').reset_index(drop=True)
    coils=pd.DataFrame(coils)
    for name,table in [('fallos',failures),('mantenimiento',maint),('paradas_linea',outages),('bobinas',coils)]:
        write(table,root/f'data/{name}.parquet')
    line=pd.DataFrame(dict(timestamp=times,estado_linea=line_state,bobina_id=coil_id,
        espesor_objetivo_mm=thick,ancho_mm=width,velocidad_salida_m_s=speed,flujo_masa_kg_s=massflow))
    line.loc[line.bobina_id==0,'bobina_id']=pd.NA
    line['bobina_id']=line.bobina_id.astype('Int64')
    write(line,root/'data/estado_linea.parquet')
    # Grade/recipe inactive rows are null: no fictitious material is rolled during downtime.
    sensor_events=[]; totals=[]
    decision_stride=cfg['decision_minutes']//step
    if cfg['decision_minutes']%step:raise ValueError('La cadencia de decisión debe ser múltiplo del paso.')
    feature_cols=None
    for a,asset in enumerate(assets.itertuples()):
        # Recompute only completed maintenance, available at the current instant.
        completed=maint.loc[maint.equipo_id==asset.equipo_id,'fin'].sort_values().astype('int64').to_numpy()
        ix=np.searchsorted(completed,times.asi8,side='right')-1
        last_end=np.full(n,times[0].value,dtype=np.int64)
        known=ix>=0;last_end[known]=completed[ix[known]]
        age[:,a]=(times.asi8-last_end)/3.6e12
        ar=lfilter([.6],[1,-.75],rng.normal(size=n))
        act=active[:,a].astype(float);load=loads[:,a]
        precursor=np.clip((dmg[:,a]-.50)/.50,0,1)**1.6
        # Hidden mode selects different non-deterministic signatures. Hidden values never join ML.
        sig=np.column_stack([precursor*(mod[:,a]==j)*act for j in range(5)])
        ambient=17+7*np.sin(2*np.pi*np.arange(n)*dt/(365.25*24))+2*np.sin(2*np.pi*np.arange(n)*dt/24)
        drift=np.clip((np.arange(n)-n*.67)/(n*.33),0,1)*rng.normal(0,.30)
        transient=(np.r_[0,np.diff(coil_id)]!=0)*act
        vib=np.maximum(.08,.3+act*(1.0+1.2*load)+sig[:,0]*2.5+sig[:,1]*1.6+sig[:,2]*.5+.20*ar+.40*transient+drift)
        temp_b=ambient+act*(21+24*load)+sig[:,0]*15+sig[:,2]*19+sig[:,4]*13+1.5*ar
        temp_m=ambient+act*(26+40*load)+sig[:,4]*28+sig[:,1]*7+2*ar
        oiltemp=ambient+act*(15+21*load)+sig[:,2]*19+sig[:,1]*7+ar
        oilpress=np.maximum(0,act*(4.3-2.0*sig[:,2])+rng.normal(0,.12,n))
        hydpress=np.maximum(0,act*(185+15*load-48*sig[:,3])+rng.normal(0,3,n))
        cool=np.maximum(0,act*(90+95*load-65*sig[:,4])+rng.normal(0,4,n))
        currentpct=np.maximum(0,act*(20+75*load+10*sig[:,1])+rng.normal(0,2,n))
        rpm=np.maximum(0,act*(750+450*load)+rng.normal(0,6,n))
        power=asset.potencia_nominal_kw*load*(1+.04*ar)
        rollforce=np.full(n,np.nan);hout=np.full(n,np.nan);hin=np.full(n,np.nan);vin=np.full(n,np.nan);vout=np.full(n,np.nan)
        striptemp=np.full(n,np.nan)
        if asset.tipo_equipo=='caja_laminacion':
            pos=int(asset.equipo_id[1:])
            hin=60*np.power(np.maximum(thick,1)/60,(pos-1)/7)
            hout=60*np.power(np.maximum(thick,1)/60,pos/7)
            contact=np.sqrt(.35*(hin-hout)/1000)
            # Simplified rolling-force proxy, not a calibrated constitutive model.
            flowstress=45e6*products.factor_carga_demo.to_numpy()[grade]
            rollforce=(width/1000)*contact*flowstress/1e6*(1+.025*ar)
            vin=speed*np.maximum(thick,1)/hin;vout=speed*np.maximum(thick,1)/hout
            rpm=vout/.35*60/(2*np.pi)
            striptemp=entrytemp-(pos/7)*270+ar*3
            for arr in [hin,hout,vin,vout,striptemp,rollforce]:arr[act==0]=np.nan
        elif asset.tipo_equipo=='horno_tunel':striptemp=np.where(act>0,entrytemp,np.nan)
        elif asset.tipo_equipo in ['enfriamiento','bobinadora']:striptemp=np.where(act>0,620+ar*5,np.nan)
        if asset.tipo_equipo not in ['caja_laminacion','bobinadora','central_hidraulica','cizalla']:
            hydpress[:]=np.nan
        frame=pd.DataFrame(dict(equipo_id=asset.equipo_id,timestamp=times,disponible_desde=times,
            tipo_equipo=asset.tipo_equipo,estado_equipo=status[:,a],en_marcha=active[:,a],
            bobina_id=line.bobina_id,grado_acero=np.array(products.grado_acero)[grade],
            espesor_objetivo_mm=thick,ancho_mm=width,carga_relativa=load,
            horas_desde_mantenimiento=age[:,a],temperatura_ambiente_c=ambient,
            vibracion_rms_mm_s=vib,temperatura_rodamiento_c=temp_b,temperatura_motor_c=temp_m,
            temperatura_aceite_c=oiltemp,presion_aceite_bar=oilpress,presion_hidraulica_bar=hydpress,
            caudal_refrigeracion_l_min=cool,corriente_motor_pct_nominal=currentpct,velocidad_motor_rpm=rpm,
            potencia_kw=power,fuerza_laminacion_mn=rollforce,espesor_entrada_caja_mm=hin,
            espesor_salida_caja_mm=hout,velocidad_entrada_caja_m_s=vin,velocidad_salida_caja_m_s=vout,
            temperatura_material_c=striptemp))
        idle=coil_id==0
        frame.loc[idle,['grado_acero','espesor_objetivo_mm','ancho_mm']]=pd.NA
        sensors=['vibracion_rms_mm_s','temperatura_rodamiento_c','temperatura_motor_c','temperatura_aceite_c',
            'presion_aceite_bar','presion_hidraulica_bar','caudal_refrigeracion_l_min','corriente_motor_pct_nominal','velocidad_motor_rpm','potencia_kw']
        # Realistic imperfections: independent missingness, block outages, spikes, stuck sensor.
        for col in sensors:
            values=frame[col].to_numpy().copy()
            values[rng.random(n)<.004]=np.nan
            for _ in range(max(1,int(n*dt/(24*40)))):
                s=int(rng.integers(1,n-12));e=min(n,s+int(rng.integers(2,13)))
                kind=rng.choice(['sin_datos','congelado','pico'])
                if kind=='sin_datos':values[s:e]=np.nan
                elif kind=='congelado':values[s:e]=values[s-1]
                else: values[s:e]*=rng.uniform(1.7,2.5)
                sensor_events.append(dict(incidencia_id=f'S{len(sensor_events)+1:06d}',equipo_id=asset.equipo_id,
                    sensor=col,inicio=at(s),fin=at(e),tipo=kind))
            frame[col]=values
        write(frame,root/f'data/telemetria/{asset.equipo_id}.parquet')
        truth=pd.DataFrame(dict(equipo_id=asset.equipo_id,timestamp=times,dano_latente=dmg[:,a],
            modo_latente=np.array(MODES)[mod[:,a]],precursor_latente=precursor))
        write(truth,root/f'privado_no_usar_como_features/{asset.equipo_id}.parquet')
        # Current observations plus trailing statistics; no interpolation from the future.
        basecols=['equipo_id','timestamp','disponible_desde','tipo_equipo','en_marcha','grado_acero','espesor_objetivo_mm','ancho_mm','carga_relativa','horas_desde_mantenimiento','temperatura_ambiente_c']
        feat=frame[basecols+sensors].copy()
        for c in sensors[:9]:
            series=frame[c]
            feat[c+'_media_1h']=series.rolling(max(1,int(1/dt)),min_periods=1).mean()
            feat[c+'_std_1h']=series.rolling(max(2,int(1/dt)),min_periods=2).std()
            feat[c+'_media_4h']=series.rolling(max(1,int(4/dt)),min_periods=1).mean()
        feat['fraccion_marcha_4h']=frame.en_marcha.rolling(int(4/dt),min_periods=1).mean()
        feat['fraccion_ausentes_1h']=frame[sensors].isna().mean(axis=1).rolling(int(1/dt),min_periods=1).mean()
        # Structural missingness exists for hydraulic pressure outside supported assets.
        feat=feat.iloc[::decision_stride].copy()
        feat=feat[(feat.en_marcha)&(feat.timestamp>=times[0]+pd.Timedelta(hours=4))].reset_index(drop=True)
        t=feat.timestamp.astype('int64').to_numpy()
        fs=failures.loc[failures.equipo_id==asset.equipo_id].sort_values('inicio')
        fns=fs.inicio.astype('int64').to_numpy()
        idx=np.searchsorted(fns,t,side='right')
        nxt=np.full(len(t),np.iinfo('int64').max,dtype=np.int64)
        has=idx<len(fns);nxt[has]=fns[idx[has]]
        pns=np.array([at(k).value for k in pm_starts],np.int64)
        pi=np.searchsorted(pns,t,side='right');nextpm=np.full(len(t),end.value,dtype=np.int64)
        ph=pi<len(pns);nextpm[ph]=pns[pi[ph]]
        targets=feat[['equipo_id','timestamp']].copy()
        targets['proximo_fallo_id']=pd.array([fs.iloc[i].evento_id if ok else None for i,ok in zip(idx,has)],dtype='string')
        targets['horas_hasta_proximo_fallo_observado']=np.where(has,(nxt-t)/3.6e12,np.nan)
        for h in cfg['horizons_hours']:
            deadline=t+int(h*3.6e12)
            positive=(nxt<=deadline)&(nxt<nextpm)
            censored=((deadline>=end.value)|(nextpm<=deadline))&~positive
            y=np.zeros(len(t),dtype=float);y[positive]=1;y[censored]=np.nan
            targets[f'fallo_{h}h']=pd.array(y,dtype='Int8')
            targets[f'censura_{h}h']=np.where(censored,np.where(deadline>=end.value,'fin_observacion','mantenimiento_preventivo'),'ninguna')
        trainend=pd.Timestamp(cfg['train_end']);valend=pd.Timestamp(cfg['validation_end'])
        maxh=pd.Timedelta(hours=max(cfg['horizons_hours']))
        split=np.where(feat.timestamp<trainend,'train',np.where(feat.timestamp<valend,'validation','test'))
        purge=((feat.timestamp<trainend)&(feat.timestamp+maxh>=trainend))|((feat.timestamp<valend)&(feat.timestamp+maxh>=valend)&(feat.timestamp>=trainend))|(feat.timestamp+maxh>=end)
        targets['particion']=np.where(purge,'purga',split)
        write(feat,root/f'ml/features/{asset.equipo_id}.parquet')
        write(targets,root/f'ml/targets/{asset.equipo_id}.parquet')
        totals.append(dict(equipo_id=asset.equipo_id,muestras=n,decisiones=len(feat),fallos=len(fs),horas_marcha=float(active[:,a].sum()*dt)))
        if feature_cols is None:feature_cols=list(feat.columns)
        print(asset.equipo_id,'telemetria',n,'decisiones',len(feat),flush=True)
    write(pd.DataFrame(sensor_events),root/'privado_no_usar_como_features/incidencias_sensores.parquet')
    pd.DataFrame(totals).to_csv(root/'resultados/resumen_equipos.csv',index=False)
    categorical=['tipo_equipo','grado_acero']
    numeric=[c for c in feature_cols if c not in ['equipo_id','timestamp','disponible_desde','en_marcha']+categorical]
    (root/'ml/columnas_modelo.json').write_text(json.dumps(dict(numeric=numeric,categorical=categorical,
        forbidden=['equipo_id','timestamp','disponible_desde','en_marcha','bobina_id','estado_equipo','proximo_fallo_id',
        'horas_hasta_proximo_fallo_observado','dano_latente','modo_latente','precursor_latente','particion'],target='fallo_8h'),indent=2))
    (root/'resultados/resumen_generacion.json').write_text(json.dumps(dict(version=cfg['version'],seed=cfg['seed'],
        inicio=str(times[0]),fin_exclusivo=str(end),equipos=m,muestras_telemetria=n*m,decisiones=sum(x['decisiones'] for x in totals),
        bobinas=len(coils),bobinas_completas=int((coils.estado_resultado=='completa').sum()),fallos=len(failures),
        fallos_por_modo=failures.modo_fallo.value_counts().to_dict(),mantenimientos=len(maint),
        incidencias_sensores=len(sensor_events),origen='100% sintético, no calibrado a ACB'),indent=2,ensure_ascii=False))
    print('GENERACIÓN COMPLETADA',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--config');parser.add_argument('--out')
    args=parser.parse_args() # Spyder: ejecutar archivo sin argumentos.
    main(args.config,args.out)
