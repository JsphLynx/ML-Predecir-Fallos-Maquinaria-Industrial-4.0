"""Aceptación v4: identidades, temporalidad de dominios y sensibilidad.
No se entrenan modelos. La consistencia matemática no valida una planta.
"""
import argparse
import copy
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
from comun import ROOT, KEY, SIGNALS, config, dump
from fisica import schedule_physics, PHYSICS_SIGNALS

def load_module(name):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def main(root=ROOT):
    root=Path(root);c=config(root/'config/escenario.json');p=c['physics'];tests=[]
    def ck(name,ok,detail=''):
        tests.append(dict(test=name,passed=bool(ok),detail=str(detail)))
        if not ok:print('FAIL',name,detail,flush=True)
    def close(a,b):return np.allclose(a,b,rtol=3e-6,atol=1e-4,equal_nan=True)
    cfg=pd.read_parquet(root/'data/configuraciones.parquet').sort_values('valid_from')
    ck('Configuraciones PK',cfg.configuration_id.is_unique)
    ck('Configuraciones sin huecos/solapamientos',cfg.valid_to.iloc[:-1].reset_index(drop=True).equals(cfg.valid_from.iloc[1:].reset_index(drop=True)))
    ck('Configuraciones cubren observación',cfg.valid_from.iloc[0]==pd.Timestamp(c['start']) and cfg.valid_to.iloc[-1]==pd.Timestamp(c['start'])+pd.Timedelta(days=c['days']))
    sensors=pd.read_parquet(root/'data/sensores.parquet')
    ck('Contrato de todas las señales',set(sensors.variable)==set(SIGNALS))
    ck('No inventar ondas de vibración',sensors.sampling_frequency_hz.isna().all() and sensors.bandwidth_low_hz.isna().all() and sensors.bandwidth_high_hz.isna().all() and sensors.aggregation_window_seconds.isna().all())
    ck('Cadencia distinta de frecuencia de adquisición',sensors.output_interval_seconds.eq(300).all())
    stats=[]
    for path in sorted((root/'sim_truth/fisica').glob('*.parquet')):
        run=path.stem;tr=pd.read_parquet(path);tele=pd.read_parquet(root/'data/telemetria'/path.name)
        f=pd.read_parquet(root/'ml/features'/path.name)
        ck(run+' claves físicas',tr[KEY].equals(tele[KEY]))
        joined=tele[['configuration_id','timestamp']].merge(cfg,on='configuration_id',validate='many_to_one')
        ck(run+' configuración válida y conocida',((joined.timestamp>=joined.valid_from)&(joined.timestamp<joined.valid_to)&(joined.known_at<=joined.timestamp)).all())
        gear=joined.gear_ratio.to_numpy();eta=joined.transmission_efficiency.to_numpy()
        active=tele.rolling_state.isin(['arranque','sin_carga','laminacion','desaceleracion'])
        rolling=tele.rolling_state.eq('laminacion')
        ck(run+' motor/cilindro transmisión',close(tr.motor_speed_rpm,tr.roll_speed_rpm*gear))
        ck(run+' velocidad banda y deslizamiento',close(tr.loc[rolling,'strip_speed_m_s'],tr.loc[rolling,'roll_speed_rpm']*2*np.pi*p['roll_radius_m']/60*(1+p['forward_slip'])))
        ck(run+' continuidad volumétrica',close(tr.loc[rolling,'width_mm']*tr.loc[rolling,'entry_thickness_mm']*tr.loc[rolling,'strip_entry_speed_m_s'],tr.loc[rolling,'width_mm']*tr.loc[rolling,'exit_thickness_mm']*tr.loc[rolling,'strip_speed_m_s']))
        ck(run+' reducción positiva',tr.loc[rolling,'entry_thickness_mm'].gt(tr.loc[rolling,'exit_thickness_mm']).all())
        ck(run+' espesores sin producto ausentes',tr.loc[~rolling,'entry_thickness_mm'].isna().all() and tr.loc[~rolling,'strip_temperature_c'].isna().all())
        ck(run+' potencia mecánica par omega',close(tr.mechanical_power_kw,tr.motor_torque_knm*2*np.pi*tr.motor_speed_rpm/60))
        roll_kw=tr.roll_torque_knm*2*np.pi*tr.roll_speed_rpm/60
        ck(run+' transmisión y pérdidas auxiliares',close(tr.mechanical_power_kw,roll_kw/eta+active.to_numpy()*p['idle_mechanical_kw']))
        ck(run+' potencia eléctrica eficiencia',close(tr.electrical_power_kw,tr.mechanical_power_kw/tr.motor_efficiency_effective))
        ck(run+' corriente trifásica',close(tr.electrical_power_kw*1000,np.sqrt(3)*p['voltage_ll_v']*p['power_factor']*tr.current_a))
        ck(run+' carga relativa definida',close(tr.load_ratio,tr.mechanical_power_kw/p['motor_rated_mechanical_kw']))
        ck(run+' física limpia finita cuando hay banda',np.isfinite(tr.loc[rolling,list(PHYSICS_SIGNALS)].to_numpy()).all())
        ck(run+' parada sin potencia/corriente',tr.loc[~active,['mechanical_power_kw','current_a','rolling_force_kn']].eq(0).all().all())
        ck(run+' temperatura banda separada de devanado',not tele.strip_temperature_c.equals(tele.winding_temperature_c))
        ck(run+' sin identificador bobina falso','coil_id' not in tele)
        changes=tele.production_segment_id.ne(tele.production_segment_id.shift())
        ck(run+' segmentos no reaparecen',tele.loc[changes,'production_segment_id'].is_unique)
        ck(run+' contexto no es verdad latente',not set(['motor_efficiency_effective','damage_motor','health_state','y24'])&set(f))
        for cc in cfg.iloc[1:].itertuples():
            after=f[(f.timestamp>=cc.valid_from)&(f.timestamp<cc.valid_from+pd.Timedelta(minutes=25))]
            ck(run+' ventana reinicia '+cc.configuration_id,after.coverage_min_30m.le(4/6+1e-6).all())
        # Statistics of clean physical rolling state; never maxima of corrupt sensors.
        for col in ['motor_speed_rpm','roll_speed_rpm','rolling_force_kn','mechanical_power_kw','current_a']:
            a=tr.loc[rolling,col]
            stats.append(dict(run_id=run,variable=col,min=float(a.min()),median=float(a.median()),max=float(a.max()),source='sim_truth_fisica_no_calibrada'))
    # Controlled parameter sensitivity with identical exogenous RNG realization.
    n=30;times=pd.date_range(c['start'],periods=n,freq='5min');reg=np.full(n,'laminacion')
    def fixture(conf=c,w=1250.,temp_shift=0):
        cc=copy.deepcopy(conf);cc['physics']['strip_temp_min_c']+=temp_shift;cc['physics']['strip_temp_max_c']+=temp_shift
        return schedule_physics(cc,times,reg,np.full(n,3.),np.full(n,w),np.ones(n),np.random.default_rng(123),0)
    base=fixture();wide=fixture(w=1500.);hot=fixture(temp_shift=30)
    force=list(PHYSICS_SIGNALS).index('rolling_force_kn');power=list(PHYSICS_SIGNALS).index('mechanical_power_kw')
    ck('Mayor ancho aumenta fuerza a igual receta',np.all(wide[0][:,force]>base[0][:,force]))
    ck('Mayor temperatura reduce fuerza a igual receta',np.all(hot[0][:,force]<base[0][:,force]))
    modified=copy.deepcopy(c);modified['physics']['gear_ratio_before']*=1.1
    geared=fixture(modified)
    ck('Transmisión modifica rpm motor',close(geared[1],base[1]*1.1))
    ck('Transmisión conserva potencia ideal a igual eficiencia',close(geared[0][:,power],base[0][:,power]))
    # Black-box independence: changing instrumentation must not change physical events.
    gen=load_module('01_generar_dataset');short=copy.deepcopy(c);short['days']=45
    products=pd.read_parquet(root/'config/productos_base_v2.parquet')
    a=gen.simulate(short,1,products);changed=copy.deepcopy(short)
    changed['sensor_defects']['gain_std']=.15;changed['sensor_defects']['blocks_poisson_mean_per_kind']=4
    b=gen.simulate(changed,1,products)
    ck('Defectos sensor no cambian fallos',a[2].equals(b[2]))
    ck('Defectos sensor no cambian daño',a[1].equals(b[1]))
    ck('Defectos sensor cambian observaciones',not a[0][list(SIGNALS)].equals(b[0][list(SIGNALS)]))
    builder=load_module('02_construir_variables');sample=a[0].iloc[:150].copy()
    # Ensure stale values from previous domain cannot leak into the current one.
    sample.loc[sample.index[120:],'configuration_id']='CFG-TEST'
    before=builder.build_features(sample,short)
    sample.loc[sample.index[:120],list(SIGNALS)]=1e8
    after=builder.build_features(sample,short)
    cols=list(SIGNALS)+[x for x in before if '_mean_' in x or '_std_' in x or '_slope_' in x]
    mask=before.configuration_id.eq('CFG-TEST')
    ck('Nuevo dominio inmune a medidas antiguas',before.loc[mask,cols].equals(after.loc[mask,cols]))
    pd.DataFrame(stats).to_csv(root/'resultados/rangos_fisicos_limpios.csv',index=False)
    result=dict(version=c['version'],checks=len(tests),passed=sum(x['passed'] for x in tests),failed=sum(not x['passed'] for x in tests),tests=tests,
                scope='Consistencia sintética e identidades; no calibración ni validación de Sestao',models_trained=False)
    dump(result,root/'resultados/validacion_fisica.json');print({k:v for k,v in result.items() if k!='tests'},flush=True)
    if result['failed']:raise SystemExit(1)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));a=p.parse_args();main(a.root)
