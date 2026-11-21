"""EDA de control. Muestra verdad simulada solo en figura de auditoría.
Las marcas de incidentes son inyecciones conocidas, no predicciones de un modelo.
"""
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from comun import ROOT, SIGNALS, write, dump

def main(root=ROOT):
    root=Path(root);events=pd.read_parquet(root/'data/fallos.parquet')
    incidents=pd.read_parquet(root/'sim_truth/incidencias_sensores.parquet')
    rows=[];profiles=[];regimes=[]
    for p in sorted((root/'data/telemetria').glob('*.parquet')):
        t=pd.read_parquet(p)
        for col in SIGNALS:
            s=t[col];quant=s.quantile([.01,.5,.99])
            rows.append(dict(run_id=p.stem,signal=col,rows=len(s),missing=int(s.isna().sum()),
                missing_fraction=float(s.isna().mean()),min=float(s.min()),p01=float(quant.iloc[0]),
                median=float(quant.iloc[1]),p99=float(quant.iloc[2]),max=float(s.max())))
        for state,g in t.groupby('rolling_state'):
            regimes.append(dict(run_id=p.stem,rolling_state=state,rows=len(g),hours=len(g)*5/60))
        # Summaries by regime allow distinguishing workload from deterioration.
        tr=pd.read_parquet(root/f'sim_truth/estado_latente/{p.stem}.parquet')
        a=t.merge(tr[['run_id','assembly_id','timestamp','health_state']],on=['run_id','assembly_id','timestamp'],validate='one_to_one')
        g=a.groupby(['rolling_state','health_state'])[['bearing_temperature_de_c','bearing_temperature_nde_c','vibration_de_mm_s','vibration_nde_mm_s','current_a','load_ratio','motor_speed_rpm']].median().reset_index()
        g.insert(0,'run_id',p.stem);profiles.append(g)
    pd.DataFrame(rows).to_csv(root/'resultados/calidad_senales.csv',index=False)
    pd.DataFrame(regimes).to_csv(root/'resultados/regimenes.csv',index=False)
    pd.concat(profiles).to_csv(root/'resultados/perfiles_regimen_salud_RESTRINGIDO.csv',index=False)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(2,2,figsize=(14,8.5),layout='constrained');fig.patch.set_facecolor('#f5f7fa')
    fig.suptitle('Motor y rodamientos · Dataset v4.0\nDATOS 100 % SINTÉTICOS · Sin modelos entrenados',fontsize=18,fontweight='bold',color='#133047')
    count=events.groupby(['run_id','onset']).size().unstack(fill_value=0)
    count.plot.bar(stacked=True,ax=axs[0,0],color=['#167f89','#e4a14b'],rot=0)
    axs[0,0].set_title('Fallos por ejecución');axs[0,0].set_ylabel('Eventos');axs[0,0].set_xlabel('Mundos alternativos; R13-R16 reservados para estrés')
    part=pd.read_csv(root/'resultados/particiones.csv').groupby('partition')[['usable_rows','positive_rows']].sum()
    order=[x for x in ['train','validation','test','stress','excluida'] if x in part.index]
    axs[0,1].bar(order,part.loc[order,'usable_rows'],color=['#167f89','#469aa0','#76b5b5','#7566a7','#aab2bc'])
    axs[0,1].set_title('Decisiones utilizables por partición');axs[0,1].set_ylabel('Filas; las excluidas no se usan para modelar')
    q=pd.DataFrame(rows).groupby('signal').missing_fraction.mean().sort_values(ascending=False).head(6)
    axs[1,0].barh(q.index[::-1],100*q.values[::-1],color='#469aa0');axs[1,0].set_title('Ausencias observadas · seis señales con mayor proporción')
    axs[1,0].set_xlabel('% de registros; no incluye retrasos de llegada')
    rg=pd.DataFrame(regimes).groupby('rolling_state').hours.sum().sort_values()
    axs[1,1].barh(rg.index,rg.values,color='#7566a7');axs[1,1].set_title('Exposición por estado operativo');axs[1,1].set_xlabel('Horas sumadas de los 16 mundos')
    for ax in axs.flat:ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    fig.savefig(root/'resultados/resumen_dataset_v4_0.png',dpi=145);plt.close(fig)
    # Select a reproducible early bearing failure, without evaluating any prediction.
    event=events[(events.run_id=='R01')&events['mode'].eq('rodamiento_de')].iloc[0]
    t=pd.read_parquet(root/'data/telemetria/R01.parquet')
    tr=pd.read_parquet(root/'sim_truth/estado_latente/R01.parquet')
    lo=event.start-pd.Timedelta(hours=72);hi=event.end+pd.Timedelta(hours=8)
    t=t[(t.timestamp>=lo)&(t.timestamp<=hi)].copy();tr=tr[(tr.timestamp>=lo)&(tr.timestamp<=hi)]
    fig,ax=plt.subplots(5,1,figsize=(14,12),sharex=True,layout='constrained')
    fig.suptitle('Ejemplo auditado R01 · Motor y apoyos DE/NDE\nEstados de salud = verdad del simulador; no diagnóstico ni predicción',fontsize=16,fontweight='bold',color='#133047')
    panels=[(['bearing_temperature_de_c','bearing_temperature_nde_c','winding_temperature_c'],['Apoyo DE','Apoyo NDE','Devanado'],'Temperatura (°C)'),
            (['vibration_de_mm_s','vibration_nde_mm_s'],['DE','NDE'],'Vibración RMS (mm/s)'),
            (['current_a'],['Motor'],'Corriente RMS (A)'),(['load_ratio'],['Carga'],'Carga relativa'),(['motor_speed_rpm'],['Motor'],'Velocidad (rpm)')]
    for a,(cols,labels,unit) in zip(ax,panels):
        for col,label,color in zip(cols,labels,['#167f89','#7b61a8','#dc8a35']):a.plot(t.timestamp,t[col],lw=.8,label=label,color=color)
        for state,color in [('normal','#57b58b'),('degradacion','#e2a646'),('fallo','#d2565b')]:
            mask=tr.health_state.eq(state).to_numpy();start=np.flatnonzero(mask&~np.r_[False,mask[:-1]]);ends=np.flatnonzero(mask&~np.r_[mask[1:],False])+1
            for j,(s,e) in enumerate(zip(start,ends)):
                right=tr.timestamp.iloc[e] if e<len(tr) else tr.timestamp.iloc[-1]+pd.Timedelta(minutes=5)
                a.axvspan(tr.timestamp.iloc[s],right,color=color,alpha=.12,label=state if j==0 else None)
        for inc in incidents[(incidents.run_id=='R01')&(incidents.start<hi)&(incidents.end>lo)&incidents.sensor_id.isin(['S-'+x for x in cols])].itertuples():
            a.axvspan(max(lo,inc.start),min(hi,inc.end),facecolor='none',edgecolor='#5e5e5e',hatch='///',alpha=.4)
        a.axvline(event.start,color='#b63d45',ls='--',lw=1);a.set_ylabel(unit);a.grid(alpha=.13)
        a.legend(loc='upper left',fontsize=8,ncol=6)
    ax[-1].xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M',tz=__import__('datetime').timezone.utc))
    ax[-1].set_xlabel('Tiempo UTC · rayado: incidencia instrumental inyectada si coincide con esta ventana')
    fig.savefig(root/'resultados/ejemplo_motor_rodamientos_v4_0.png',dpi=145);plt.close(fig)
    dump({'example_event':event.event_id,'example_run':'R01','models_trained':False,
          'health_overlay':'Verdad simulada; prohibida como predictor','incident_overlay':'Inyecciones del simulador, no Isolation Forest'},root/'resultados/figuras.json')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));a=p.parse_args();main(a.root)
