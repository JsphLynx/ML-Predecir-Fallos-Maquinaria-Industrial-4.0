"""Auditoría de integridad, física simplificada, objetivos y fuga temporal."""
from pathlib import Path
import json
import argparse
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def main(root=ROOT, config=None):
    root=Path(root);cfg=json.loads(Path(config or root/'config/escenario.json').read_text())
    checks=[]
    def check(name, condition, detail=''):
        checks.append(dict(prueba=name,resultado='OK' if bool(condition) else 'FALLO',detalle=detail))
        if not bool(condition):print('FALLO:',name,detail,flush=True)
    assets=pd.read_parquet(root/'data/equipos.parquet')
    failures=pd.read_parquet(root/'data/fallos.parquet')
    maint=pd.read_parquet(root/'data/mantenimiento.parquet')
    coils=pd.read_parquet(root/'data/bobinas.parquet')
    line=pd.read_parquet(root/'data/estado_linea.parquet')
    check('PK equipos',assets.equipo_id.is_unique)
    for name,col,df in [('fallos','evento_id',failures),('mantenimiento','mantenimiento_id',maint),('bobinas','bobina_id',coils)]:
        check(f'PK {name}',df[col].is_unique and df[col].notna().all())
    for name,df in [('fallos',failures),('mantenimiento',maint)]:
        check(f'FK {name}',df.equipo_id.isin(assets.equipo_id).all())
        check(f'intervalos {name}',(df.fin>df.inicio).all())
    corr=maint[maint.tipo=='correctivo']
    check('cada fallo tiene exactamente una reparación',corr.evento_id.is_unique and set(corr.evento_id)==set(failures.evento_id))
    check('masa máxima bobina',coils.masa_objetivo_t.le(28.0001).all())
    check('rango espesor 1-15 mm',coils.espesor_objetivo_mm.between(1,15).all())
    calc=7850*coils.ancho_mm/1000*coils.espesor_objetivo_mm/1000*coils.longitud_objetivo_m/1000
    check('masa geometría bobina',np.allclose(calc,coils.masa_objetivo_t,rtol=2e-6))
    check('procesado no excede objetivo',coils.pasos_procesados.le(coils.pasos_objetivo).all())
    check('producción nula en parada',line.loc[line.estado_linea!=0,'flujo_masa_kg_s'].eq(0).all())
    check('bobina FK temporal',set(line.bobina_id.dropna())<=set(coils.bobina_id))
    end=pd.Timestamp(cfg['end_exclusive']);step=cfg['step_minutes']
    expected=len(pd.date_range(cfg['start'],end,freq=f'{step}min',inclusive='left'))
    splits=[];total_missing=0;total_sensor=0
    columns=json.loads((root/'ml/columnas_modelo.json').read_text())
    for a in assets.itertuples():
        tele=pd.read_parquet(root/f'data/telemetria/{a.equipo_id}.parquet')
        features=pd.read_parquet(root/f'ml/features/{a.equipo_id}.parquet')
        targets=pd.read_parquet(root/f'ml/targets/{a.equipo_id}.parquet')
        check(a.equipo_id+' telemetría cardinalidad y clave',len(tele)==expected and not tele.duplicated(['equipo_id','timestamp']).any())
        check(a.equipo_id+' cadencia',tele.timestamp.diff().dropna().eq(pd.Timedelta(minutes=step)).all())
        check(a.equipo_id+' disponible en t',features.disponible_desde.le(features.timestamp).all())
        check(a.equipo_id+' modelos no usan verdad/targets',not(set(columns['numeric']+columns['categorical'])&set(columns['forbidden'])) and not any(c.startswith(('fallo_','censura_')) for c in features.columns))
        check(a.equipo_id+' ausencia de infinitos',not np.isinf(tele.select_dtypes('number').to_numpy(dtype=float)).any())
        keys=['equipo_id','timestamp']
        joined=features.merge(targets.sample(frac=1,random_state=9),on=keys,how='left',validate='one_to_one',indicator=True)
        check(a.equipo_id+' join resistente a orden',len(joined)==len(features) and joined['_merge'].eq('both').all())
        f=failures[failures.equipo_id==a.equipo_id].sort_values('inicio')
        check(a.equipo_id+' modo admisible',f.modo_fallo.isin(a.modos_admisibles.split('|')).all())
        # Reconstruct each target from interval comparisons, independent of searchsorted code.
        t=joined.timestamp
        ownpm=maint[(maint.equipo_id==a.equipo_id)&(maint.tipo=='preventivo')]
        for h in cfg['horizons_hours']:
            limit=t+pd.Timedelta(hours=h)
            pos=np.zeros(len(t),bool);cen=(limit>=end).to_numpy()
            for event in f.itertuples():pos|=((t<event.inicio)&(limit>=event.inicio)).to_numpy()
            for pm in ownpm.itertuples():
                before=((t<pm.inicio)&(limit>=pm.inicio)).to_numpy()
                # Count positive only if a failure is before the earliest preventive intervention.
                fp=np.zeros(len(t),bool)
                for event in f[(f.inicio>=pm.inicio)&(f.inicio<=pm.inicio+pd.Timedelta(hours=h))].itertuples():
                    fp|=((t<event.inicio)&(limit>=event.inicio)).to_numpy()
                pos[before&fp]=False
                cen|=before
            truth=np.where(pos,1,np.where(cen,np.nan,0))
            observed=joined[f'fallo_{h}h'].to_numpy(dtype=float,na_value=np.nan)
            check(a.equipo_id+f' etiquetas {h}h y censura',np.allclose(truth,observed,equal_nan=True))
        for split,bound in [('train',cfg['train_end']),('validation',cfg['validation_end']),('test',cfg['end_exclusive'])]:
            rows=joined[joined.particion==split]
            check(a.equipo_id+f' purga {split}',(rows.timestamp+pd.Timedelta(hours=max(cfg['horizons_hours']))<pd.Timestamp(bound)).all())
        # Recompute trailing mean directly on causal prefix; values after decision cannot affect it.
        sample=features.iloc[::max(1,len(features)//25)]
        for row in sample.itertuples():
            hist=tele[(tele.timestamp>row.timestamp-pd.Timedelta(hours=1))&(tele.timestamp<=row.timestamp)]
            expected_mean=hist.vibracion_rms_mm_s.mean()
            if not np.isclose(expected_mean,row.vibracion_rms_mm_s_media_1h,rtol=2e-6,equal_nan=True):
                check(a.equipo_id+' rolling causal',False);break
        else:check(a.equipo_id+' rolling causal',True)
        if a.tipo_equipo=='caja_laminacion':
            run=tele[tele.en_marcha]
            check(a.equipo_id+' reducción espesor',(run.espesor_entrada_caja_mm>run.espesor_salida_caja_mm).all())
            check(a.equipo_id+' conservación flujo',np.allclose(run.espesor_entrada_caja_mm*run.velocidad_entrada_caja_m_s,run.espesor_salida_caja_mm*run.velocidad_salida_caja_m_s,rtol=3e-6))
        for event in f.itertuples():
            prev=tele[tele.timestamp==event.inicio-pd.Timedelta(minutes=step)]
            check(event.evento_id+' fallo precedido de marcha',len(prev)==1 and bool(prev.en_marcha.iloc[0]))
        for split,g in joined.groupby('particion'):
            splits.append(dict(equipo_id=a.equipo_id,particion=split,filas=len(g),positivos_8h=int(g.fallo_8h.sum()),censurados_8h=int(g.fallo_8h.isna().sum())))
        total_missing+=int(tele.vibracion_rms_mm_s.isna().sum());total_sensor+=len(tele)
    summary=pd.DataFrame(splits)
    for split in ['train','validation','test']:
        s=summary[summary.particion==split]
        check('positivos en '+split,s.positivos_8h.sum()>0)
    summary.to_csv(root/'resultados/distribucion_particiones.csv',index=False)
    result=dict(comprobaciones=len(checks),correctas=sum(x['resultado']=='OK' for x in checks),
        fallidas=sum(x['resultado']=='FALLO' for x in checks),fraccion_ausente_vibracion=total_missing/total_sensor,
        alcance='Consistencia del escenario sintético; no validación industrial ni exhaustividad física.',pruebas=checks)
    (root/'resultados/validacion.json').write_text(json.dumps(result,indent=2,ensure_ascii=False))
    print(json.dumps({k:v for k,v in result.items() if k!='pruebas'},ensure_ascii=False),flush=True)
    if result['fallidas']:raise SystemExit(1)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));p.add_argument('--config');a=p.parse_args();main(a.root,a.config)
