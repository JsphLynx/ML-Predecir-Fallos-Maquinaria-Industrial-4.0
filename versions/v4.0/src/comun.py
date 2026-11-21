"""Contrato compartido, sin dependencias de datos privados al construir variables."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ASSEMBLY = 'DEMO-C01-DRV01'
MOTOR = 'DEMO-C01-M01'
DE = 'DEMO-C01-BRG-DE'
NDE = 'DEMO-C01-BRG-NDE'
KEY = ['run_id', 'assembly_id', 'timestamp']
SIGNALS = {
    'bearing_temperature_de_c': ('°C', -30, 250, DE, 'Temperatura del apoyo DE'),
    'bearing_temperature_nde_c': ('°C', -30, 250, NDE, 'Temperatura del apoyo NDE'),
    'winding_temperature_c': ('°C', -30, 300, MOTOR, 'Temperatura del devanado'),
    'vibration_de_mm_s': ('mm/s', 0, 40, DE, 'Velocidad vibratoria RMS DE'),
    'vibration_nde_mm_s': ('mm/s', 0, 40, NDE, 'Velocidad vibratoria RMS NDE'),
    'acceleration_de_m_s2': ('m/s²', 0, 200, DE, 'Aceleración RMS DE'),
    'acceleration_nde_m_s2': ('m/s²', 0, 200, NDE, 'Aceleración RMS NDE'),
    'kurtosis_de': ('adimensional', 1, 80, DE, 'Curtosis de Pearson DE, descriptor simulado'),
    'kurtosis_nde': ('adimensional', 1, 80, NDE, 'Curtosis de Pearson NDE, descriptor simulado'),
    'current_a': ('A', 0, 6000, MOTOR, 'Corriente RMS derivada de potencia/tensión/PF supuestos'),
    'load_ratio': ('fracción', 0, 1.5, MOTOR, 'Carga relativa observable simulada'),
    'motor_speed_rpm': ('rpm', 0, 2400, MOTOR, 'Velocidad de eje motor supuesta, no de cilindro'),
    'ambient_temperature_c': ('°C', -30, 70, ASSEMBLY, 'Temperatura ambiente'),
    'cooling_flow_l_min': ('L/min', 0, 500, MOTOR, 'Caudal de refrigeración supuesto'),
    'lubrication_pressure_bar': ('bar', 0, 15, ASSEMBLY, 'Presión del circuito de lubricación supuesto'),
}
from fisica import PHYSICS_SIGNALS
SIGNALS.update({k:(v[0],v[1],v[2],ASSEMBLY,v[3]) for k,v in PHYSICS_SIGNALS.items()})
SIGNALS['load_ratio']=('fracción',0,4,MOTOR,'Potencia mecánica / potencia nominal demo')
SIGNALS['motor_speed_rpm']=('rpm',0,4000,MOTOR,'Velocidad de eje motor; distinta del cilindro')

ESSENTIAL = list(SIGNALS)[:5] + ['current_a', 'load_ratio', 'motor_speed_rpm']

def config(path=None):
    c = json.loads(Path(path or ROOT/'config/escenario.json').read_text(encoding='utf-8'))
    if (c['step_minutes'], c['decision_minutes']) != (5, 15):
        raise ValueError('Contrato v4: telemetría 5 min / decisiones 15 min.')
    if not 1 <= c['base_runs'] < c['runs']:
        raise ValueError('Se requieren ejecuciones base y estrés separadas.')
    return c

def write(df, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = df.copy()
    for col in df.select_dtypes(include='float64'):
        df[col] = df[col].astype('float32')
    df.to_parquet(path, index=False, compression='zstd')

def dump(obj, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False)+'\n', encoding='utf-8')

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()

def empty_events(rows, columns, dates):
    frame = pd.DataFrame(rows, columns=columns)
    for col in dates:
        frame[col] = pd.to_datetime(frame[col], utc=True)
    return frame
