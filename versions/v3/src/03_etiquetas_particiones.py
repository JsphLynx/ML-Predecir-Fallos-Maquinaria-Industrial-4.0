"""Etiquetas retrospectivas. Este script es el único constructor ML que lee verdad.
No entrenar con ninguna columna de esta tabla excepto y24 como objetivo.
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from comun import ROOT, KEY, config, write, dump

def make_targets(f, events, maint, truth, episodes, incidents, c, number):
    t=f.timestamp;end=pd.Timestamp(c['start'])+pd.Timedelta(days=c['days'])
    horizon=pd.Timedelta(hours=c['horizon_hours']);limit=t+horizon
    y=np.zeros(len(f),dtype=float);reason=np.full(len(f),'ninguna',dtype=object)
    nexte=np.full(len(f),end.value+int(horizon.value),dtype='int64')
    event_id=np.full(len(f),None,dtype=object)
    for event in events.sort_values('start',ascending=False).itertuples():
        mask=(t<event.start).to_numpy();nexte[mask]=event.start.value;event_id[mask]=event.event_id
    nextpm=np.full(len(f),np.iinfo('int64').max,dtype='int64')
    for pm in maint[maint.kind=='preventivo'].sort_values('start',ascending=False).itertuples():
        nextpm[(t<pm.start).to_numpy()]=pm.start.value
    positive=(nexte<=limit.astype('int64').to_numpy())&(nexte<nextpm)&(nexte<end.value)
    # End-exclusive observation: an event exactly at end is not observed.
    cen_end=(limit>=end).to_numpy();cen_pm=(nextpm<=limit.astype('int64').to_numpy())
    y[positive]=1
    censored=~positive&(cen_end|cen_pm);y[censored]=np.nan
    reason[censored]=np.where(nextpm[censored]<end.value,'mantenimiento_preventivo','fin_observacion')
    ineligible=~f.eligible_operation.to_numpy();y[ineligible]=np.nan;reason[ineligible]='regimen_no_elegible'
    out=f[KEY].copy();out['y24']=pd.array(y,dtype='Int8');out['censor_reason']=reason
    out['event_id']=pd.array(np.where(y==1,event_id,None),dtype='string')
    b1=pd.Timestamp(c['start'])+pd.Timedelta(days=c['days']*c['train_fraction'])
    b2=b1+pd.Timedelta(days=c['days']*c['validation_fraction'])
    split=np.where(t<b1,'train',np.where(t<b2,'validation','test')).astype(object)
    exclude=np.full(len(f),'ninguno',dtype=object)
    if number>c['base_runs']:
        split[:]='stress'
    else:
        for boundary in [b1,b2]:
            gap=((t<boundary)&(t+pd.Timedelta(hours=c['purge_hours'])>=boundary)).to_numpy()
            exclude[gap]='purga_28h';split[gap]='excluida'
            # Exclude the whole latent degradation episode when it crosses a boundary.
            for ep in episodes[(episodes.start<boundary)&(episodes.end>boundary)].itertuples():
                mask=((t>=ep.start-horizon)&(t<ep.end)).to_numpy()
                exclude[mask]='episodio_cruza_frontera';split[mask]='excluida'
    warm=(t<pd.Timestamp(c['start'])+pd.Timedelta(hours=c['warmup_hours'])).to_numpy()
    split[warm]='excluida';exclude[warm]='calentamiento'
    out['partition']=split;out['exclusion_reason']=exclude
    truth_dec=f[KEY].merge(truth[KEY+['health_state']],on=KEY,validate='one_to_one')
    reference=truth_dec.health_state.eq('normal').to_numpy()
    # Simulator-assisted clean reference is for training IF only; not available in service.
    for incident in incidents.itertuples():
        reference[((t>=incident.start)&(t<incident.end+pd.Timedelta(hours=4))).to_numpy()]=False
    out['healthy_reference_if']=reference&f.evaluation_status.eq('evaluable').to_numpy()&(split=='train')
    return out

def main(root=ROOT):
    root=Path(root);c=config(root/'config/escenario.json')
    tables={name:pd.read_parquet(root/folder/f'{name}.parquet') for name,folder in [
        ('fallos','data'),('mantenimiento','data'),('episodios','sim_truth'),('incidencias_sensores','sim_truth')]}
    summary=[]
    for number,path in enumerate(sorted((root/'ml/features').glob('*.parquet')),1):
        run=path.stem;f=pd.read_parquet(path);tr=pd.read_parquet(root/f'sim_truth/estado_latente/{run}.parquet')
        t=make_targets(f,*[tables[k][tables[k].run_id==run] for k in ['fallos','mantenimiento']],tr,
            *[tables[k][tables[k].run_id==run] for k in ['episodios','incidencias_sensores']],c,number)
        write(t,root/'ml/targets'/path.name)
        joined=f[KEY+['evaluation_status']].merge(t,on=KEY,validate='one_to_one')
        for part,g in joined.groupby('partition'):
            usable=g[g.evaluation_status.eq('evaluable')&g.y24.notna()]
            summary.append(dict(run_id=run,partition=part,rows=len(g),censored=int(g.y24.isna().sum()),
                usable_rows=len(usable),positive_rows=int(usable.y24.sum()),positive_events=int(usable.event_id.nunique()),
                healthy_if=int(g.healthy_reference_if.sum())))
    summary=pd.DataFrame(summary);summary.to_csv(root/'resultados/particiones.csv',index=False)
    dump({'horizon_hours':24,'step_minutes':5,'decision_minutes':15,'purge_hours':28,
        'partition_rows':summary.groupby('partition').rows.sum().to_dict(),
        'usable_rows':summary.groupby('partition').usable_rows.sum().to_dict(),
        'excluded_episode_policy':'Excluir episodios latentes completos que crucen fronteras y las 24 h previas.',
        'no_model_training':True},root/'resultados/etiquetas.json')
    print(summary.groupby('partition')[['rows','usable_rows','positive_rows','positive_events']].sum().to_string(),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));a=p.parse_args();main(a.root)
