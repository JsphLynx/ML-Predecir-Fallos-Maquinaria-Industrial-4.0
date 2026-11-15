"""Figura de control del escenario sintético; guardar en resultados."""
from pathlib import Path
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
ROOT=Path(__file__).resolve().parents[1]

def main():
    events=pd.read_parquet(ROOT/'data/fallos.parquet')
    coils=pd.read_parquet(ROOT/'data/bobinas.parquet')
    models=json.loads((ROOT/'resultados/modelo_base.json').read_text())['modelos']
    fig,axes=plt.subplots(2,2,figsize=(15,9),layout='constrained')
    fig.patch.set_facecolor('#f3f5f7')
    for ax in axes.flat:
        ax.set_facecolor('white');ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    fig.suptitle('ACB / Sestao · Escenario sintético para mantenimiento predictivo\n18 meses · 18 equipos · Datos inventados, sin calibración industrial',fontsize=18,fontweight='bold',color='#102b40')
    ax=axes[0,0];count=events.modo_fallo.value_counts().sort_values()
    ax.barh(count.index,count.values,color='#126c82');ax.set_title('210 averías simuladas por mecanismo',loc='left',fontweight='bold');ax.set_xlabel('Eventos, no filas de sensores');ax.grid(axis='x',alpha=.15)
    ax=axes[0,1];counts=coils[coils.estado_resultado=='completa'].espesor_objetivo_mm.value_counts().sort_index()
    ax.bar([f'{x:.3g}' for x in counts.index],counts,color='#dc7546')
    ax.set_title('Bobinas completas por espesor objetivo',loc='left',fontweight='bold');ax.set_xlabel('Espesor (mm)');ax.set_ylabel('Bobinas simuladas')
    ax=axes[1,0]
    sample=events[(events.equipo_id=='F3')&(events.tipo_inicio=='progresivo')].iloc[0]
    t=pd.read_parquet(ROOT/'data/telemetria/F3.parquet');t=t[(t.timestamp>=sample.inicio-pd.Timedelta(hours=48))&(t.timestamp<=sample.fin+pd.Timedelta(hours=6))]
    ax.plot(t.timestamp,t.vibracion_rms_mm_s,color='#126c82',lw=1,label='RMS observado')
    ax.axvline(sample.inicio,color='#c9503d',ls='--',label='Inicio avería');ax.axvspan(sample.inicio,sample.fin,alpha=.1,color='#c9503d')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %Hh'));ax.tick_params(axis='x',rotation=20);ax.set_ylabel('Vibración (mm/s)');ax.set_title('Ejemplo F3: señal, avería y reparación',loc='left',fontweight='bold');ax.legend(fontsize=8)
    ax=axes[1,1];labels=['ML','Regla','Sin avisos'];names=['hist_gradient_boosting','regla_estadistica','sin_avisos']
    det=[models[x]['test']['eventos_detectados'] for x in names];false=[models[x]['test']['falsas_alertas'] for x in names];x=np.arange(3)
    ax.bar(x-.18,det,width=.36,color='#126c82',label='Fallos detectados (de 34)');ax.bar(x+.18,false,width=.36,color='#dc7546',label='Falsas alertas')
    ax.set_xticks(x,labels);ax.set_title('Prueba temporal reservada · horizonte 8 h',loc='left',fontweight='bold');ax.legend(fontsize=8);ax.set_ylabel('Eventos / episodios')
    ax.text(.02,-.20,'Umbrales elegidos en validación; distinta carga de avisos.\nRendimiento del simulador, no de la planta real.',transform=ax.transAxes,fontsize=9,color='#526575')
    fig.savefig(ROOT/'resultados/resumen_visual.png',dpi=140,bbox_inches='tight');plt.close(fig)
if __name__=='__main__':main()
