"""Snapshots causales cada 15 minutos. No lee sim_truth ni etiquetas.
Cada estadístico exige observed_at <= decisión y available_at <= decisión.
"""
import argparse
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
from comun import ROOT, KEY, SIGNALS, ESSENTIAL, config, write, dump

def build_features(tele, c):
    tele=tele.sort_values('timestamp').reset_index(drop=True)
    n=len(tele);stride=c['decision_minutes']//c['step_minutes']
    decision=np.arange(0,n,stride);length=240//c['step_minutes']
    raw_ix=decision[:,None]-np.arange(length-1,-1,-1)[None,:]
    ix=np.maximum(raw_ix,0)
    obs=tele.timestamp.astype('int64').to_numpy()
    avail=tele.available_at.astype('int64').to_numpy()
    cutoff=obs[decision]
    present=(raw_ix>=0)&(avail[ix]<=cutoff[:,None])
    matrix=tele[list(SIGNALS)].to_numpy(dtype=float)
    low=np.array([v[1] for v in SIGNALS.values()]);high=np.array([v[2] for v in SIGNALS.values()])
    bad=(matrix<low)|(matrix>high)
    matrix[bad]=np.nan
    hist=matrix[ix].copy();hist[~present]=np.nan
    invalid=bad[ix]&present[:,:,None]
    essential_idx=[list(SIGNALS).index(x) for x in ESSENTIAL]
    out=tele.iloc[decision][KEY+['rolling_state','steel_family','target_thickness_mm','width_mm',
        'run_hours_since_service','known_service_type','starts_last_24h']].reset_index(drop=True).copy()
    # Most recent valid reading per signal, at most 10 min old. No backfill.
    positions=np.where(np.isfinite(hist),np.arange(length)[None,:,None],-1).max(axis=1)
    ages=(length-1-positions)*c['step_minutes']
    current=np.take_along_axis(hist,np.maximum(positions,0)[:,None,:],axis=1)[:,0,:]
    current[(positions<0)|(ages>c['max_data_age_minutes'])]=np.nan
    values={col:current[:,j] for j,col in enumerate(SIGNALS)}
    for minutes in c['windows_minutes']:
        steps=minutes//c['step_minutes'];a=hist[:,-steps:,:]
        valid=np.isfinite(a);count=valid.sum(axis=1)
        safe=np.where(valid,a,0)
        mean=np.divide(safe.sum(axis=1),count,out=np.full_like(count,np.nan,dtype=float),where=count>0)
        ss=np.where(valid,(a-mean[:,None,:])**2,0).sum(axis=1)
        std=np.sqrt(np.divide(ss,count-1,out=np.full_like(ss,np.nan),where=count>1))
        x=np.arange(steps)*c['step_minutes']/60
        sx=(valid*x[None,:,None]).sum(axis=1);sxx=(valid*x[None,:,None]**2).sum(axis=1)
        sy=safe.sum(axis=1);sxy=(safe*x[None,:,None]).sum(axis=1)
        den=count*sxx-sx**2
        slope=np.divide(count*sxy-sx*sy,den,out=np.full_like(den,np.nan),where=(count>1)&(den>1e-10))
        for j,col in enumerate(SIGNALS):
            for suffix,v in [('mean',mean),('std',std),('slope_per_h',slope)]:
                values[f'{col}_{suffix}_{minutes}m']=v[:,j]
    coverage=np.isfinite(hist[:,-6:,essential_idx]).sum(axis=1)/6
    out['coverage_min_30m']=coverage.min(axis=1)
    out['missing_fraction_30m']=1-np.isfinite(hist[:,-6:,:]).mean(axis=(1,2))
    out['out_of_range_fraction_30m']=invalid[:,-6:,:].mean(axis=(1,2))
    last6=hist[:,-6:,essential_idx]
    full=np.isfinite(last6).all(axis=1)
    # Frozen signal detection uses only arrived values, during a stable active regime.
    same_regime=(tele.rolling_state.to_numpy()[ix[:,-6:]]==out.rolling_state.to_numpy()[:,None]).all(axis=1)
    frozen=full&(np.nan_to_num(last6).max(axis=1)==np.nan_to_num(last6).min(axis=1))
    out['sensor_stale']=frozen.any(axis=1)&same_regime&out.rolling_state.isin(c['eligible_regimes']).to_numpy()
    out['max_data_age_minutes']=np.where((positions[:,essential_idx]>=0).all(axis=1),ages[:,essential_idx].max(axis=1),np.nan)
    max_avail=np.where(present,avail[ix],np.iinfo('int64').min).max(axis=1)
    out['source_available_at_max']=pd.to_datetime(max_avail,utc=True)
    out['eligible_operation']=out.rolling_state.isin(c['eligible_regimes'])
    warmup=out.timestamp>=tele.timestamp.iloc[0]+pd.Timedelta(hours=c['warmup_hours'])
    coverage_ok=out.coverage_min_30m>=c['coverage_min']
    age_ok=out.max_data_age_minutes.le(c['max_data_age_minutes'])
    out['evaluation_status']=np.select([
        ~out.eligible_operation,~warmup,~coverage_ok,~age_ok,out.sensor_stale],
        ['regimen_no_elegible','calentamiento','cobertura_insuficiente','dato_antiguo','sensor_congelado'],default='evaluable')
    out['quality_code']=np.select([~coverage_ok,~age_ok,out.sensor_stale,out.out_of_range_fraction_30m.gt(0)],
        ['cobertura_insuficiente','dato_antiguo','sensor_congelado','fuera_rango'],default='ok')
    # A sensor outside the configured range is quality evidence, never a failure label.
    return pd.concat([out,pd.DataFrame(values)],axis=1)

def main(root=ROOT):
    root=Path(root);c=config(root/'config/escenario.json')
    total=0;statuses={}
    for path in sorted((root/'data/telemetria').glob('*.parquet')):
        f=build_features(pd.read_parquet(path),c);write(f,root/'ml/features'/path.name)
        total+=len(f)
        for k,v in f.evaluation_status.value_counts().items():statuses[k]=statuses.get(k,0)+int(v)
        print(path.stem,'decisiones',len(f),'evaluables',int(f.evaluation_status.eq('evaluable').sum()),flush=True)
    numeric=list(SIGNALS)+[f'{s}_{stat}_{w}m' for w in c['windows_minutes'] for s in SIGNALS for stat in ['mean','std','slope_per_h']]
    numeric+=['target_thickness_mm','width_mm','run_hours_since_service','starts_last_24h','missing_fraction_30m']
    categorical=['rolling_state','steel_family','known_service_type']
    forbidden=[x for x in f.columns if x not in numeric+categorical]+['health_state','damage_de','damage_nde','damage_motor',
        'y24','censor_reason','event_id','partition','scenario','healthy_reference_if','episode_id','future_failure_at']
    dump(dict(numeric=numeric,categorical=categorical,forbidden=forbidden,target='y24',keys=KEY,
        use_rows="evaluation_status == 'evaluable' AND y24 NOT NULL AND partition in train/validation/test",
        isolation_forest="Solo train evaluable con healthy_reference_if; selector simulado retrospectivo, nunca predictor.",
        models_trained=False),root/'ml/columnas_modelo.json')
    dump(dict(decision_rows=total,evaluation_status=statuses,numeric_predictors=len(numeric),categorical_predictors=len(categorical)),root/'resultados/variables.json')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));a=p.parse_args();main(a.root)
