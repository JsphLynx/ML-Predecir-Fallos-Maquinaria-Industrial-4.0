"""Modelo mínimo cuasiestático, didáctico y sin calibración industrial.

F = sigma * ancho * sqrt(R * delta_h) * factor_forma.
Par equivalente de DOS cilindros = 2 * F * brazo * longitud_contacto.
No resuelve elasticidad, tensiones entre cajas, mordida ni dinámica torsional.
Las identidades se verifican en sim_truth, antes de defectos de medida.
"""
import numpy as np
import pandas as pd

PHYSICS_SIGNALS = {
    'roll_speed_rpm': ('rpm', 0, 1000, 'Velocidad de cilindros equivalentes'),
    'strip_speed_m_s': ('m/s', 0, 25, 'Velocidad de banda a la salida'),
    'strip_entry_speed_m_s': ('m/s', 0, 25, 'Velocidad de banda a la entrada'),
    'entry_thickness_mm': ('mm', 0, 40, 'Espesor de entrada de esta caja equivalente'),
    'exit_thickness_mm': ('mm', 0, 30, 'Espesor de salida de esta caja equivalente'),
    'strip_temperature_c': ('°C', 0, 1400, 'Temperatura de banda; no de motor ni apoyo'),
    'rolling_force_kn': ('kN', 0, 50000, 'Fuerza separadora por modelo simplificado'),
    'roll_torque_knm': ('kNm', 0, 3000, 'Par equivalente total de dos cilindros'),
    'motor_torque_knm': ('kNm', 0, 1000, 'Par de eje motor equivalente'),
    'mechanical_power_kw': ('kW', 0, 15000, 'Potencia mecánica a la salida del motor'),
    'electrical_power_kw': ('kW', 0, 20000, 'Potencia activa eléctrica de entrada al motor'),
}

def configurations(c):
    """Intervalos [valid_from, valid_to), conocidos al inicio de cada dominio."""
    p=c['physics'];start=pd.Timestamp(c['start']);end=start+pd.Timedelta(days=c['days'])
    change=start+pd.Timedelta(days=p['configuration_change_day'])
    rows=[]
    for i,(a,b) in enumerate([(start,min(change,end)),(change,end)]):
        if a>=b:continue
        rows.append(dict(configuration_id=f'CFG-{i+1:02d}',stand_id=p['stand_id'],
            valid_from=a,valid_to=b,known_at=a,
            drive_version=f'DRIVE-DEMO-{i+1}',control_version=f'CONTROL-DEMO-{i+1}',
            sensor_version=f'SENSOR-DEMO-{i+1}',maintenance_policy_version='PM-DEMO-1',
            roll_radius_m=p['roll_radius_m'],gear_ratio=p['gear_ratio_before' if i==0 else 'gear_ratio_after'],
            transmission_efficiency=p['transmission_efficiency'],
            motor_efficiency=p['motor_efficiency_before' if i==0 else 'motor_efficiency_after'],
            voltage_ll_v=p['voltage_ll_v'],power_factor=p['power_factor'],
            rated_mechanical_kw=p['motor_rated_mechanical_kw'],forward_slip=p['forward_slip'],
            sensor_gain=1.0 if i==0 else p['sensor_gain_after'],
            evidence_status='supuesto_demo_no_calibrado',is_synthetic=True))
    return pd.DataFrame(rows)

def schedule_physics(c,times,regime,thickness,width,grade_factor,rng,variant):
    """Receta exógena: no recibe daño, fallos, etiquetas ni datos futuros."""
    p=c['physics'];n=len(times);rolling=regime=='laminacion'
    change=pd.Timestamp(c['start'])+pd.Timedelta(days=p['configuration_change_day'])
    domain=np.asarray(times>=change)
    gear=np.where(domain,p['gear_ratio_after'],p['gear_ratio_before'])
    eta=np.where(domain,p['motor_efficiency_after'],p['motor_efficiency_before'])
    reduction=rng.uniform(p['reduction_min'],p['reduction_max'],n)
    temp=rng.uniform(p['strip_temp_min_c'],p['strip_temp_max_c'],n)
    output=np.asarray(thickness,float);entry=output/(1-reduction)
    speed=np.clip(p['strip_speed_coefficient']/np.sqrt(np.where(rolling,output,1)),
                  p['strip_speed_min_m_s'],p['strip_speed_max_m_s'])*(1.08 if variant==1 else 1)
    speed=np.where(rolling,speed,0.)
    radius=p['roll_radius_m'];contact=np.sqrt(np.maximum(0,radius*(entry-output)/1000))
    flow_stress=p['flow_stress_mpa_at_900c']*1e6*grade_factor*np.exp(-p['temperature_coefficient_per_c']*(temp-900))
    force=np.where(rolling,flow_stress*width/1000*contact*p['force_shape_factor'],0.)
    roll_torque=2*force*np.nan_to_num(contact)*p['torque_lever_factor']
    roll_rpm=speed/(2*np.pi*radius*(1+p['forward_slip']))*60
    # Idle/start/deceleration values are operating setpoints, not strip speeds.
    for state,rpm in [('arranque',45.),('sin_carga',90.),('desaceleracion',35.)]:
        roll_rpm=np.where(regime==state,rpm,roll_rpm)
    motor_rpm=roll_rpm*gear;omega=2*np.pi*motor_rpm/60
    motor_power=roll_torque*(2*np.pi*roll_rpm/60)/p['transmission_efficiency']/1000
    motor_power+=np.where(motor_rpm>0,p['idle_mechanical_kw'],0.)
    motor_torque=np.divide(motor_power,omega,out=np.zeros(n),where=omega>0) # kNm
    vals={
        'roll_speed_rpm':roll_rpm,'strip_speed_m_s':speed,
        'strip_entry_speed_m_s':np.where(rolling,speed*output/entry,0.),
        'entry_thickness_mm':np.where(rolling,entry,0.),'exit_thickness_mm':np.where(rolling,output,0.),
        'strip_temperature_c':np.where(rolling,temp,0.),'rolling_force_kn':force/1000,
        'roll_torque_knm':roll_torque/1000,'motor_torque_knm':motor_torque,
        'mechanical_power_kw':motor_power,'electrical_power_kw':motor_power/eta}
    matrix=np.column_stack([vals[k] for k in PHYSICS_SIGNALS])
    return matrix,motor_rpm,motor_power/p['motor_rated_mechanical_kw'],eta,domain

def sensor_contract(signals):
    """No inventa una adquisición de alta frecuencia que no existe."""
    rows=[]
    for name,v in signals.items():
        vibration=name.startswith(('vibration','acceleration','kurtosis'))
        rows.append(dict(sensor_id='S-'+name,asset_id=v[3],variable=name,unit=v[0],
            min_demo=v[1],max_demo=v[2],method='descriptor_sintetico_sin_onda',is_synthetic=True,
            descriptor_type='Pearson_kurtosis' if name.startswith('kurtosis') else 'RMS' if vibration else 'instantaneous_simulated',
            axis='no_especificado',mounting='no_especificado',sampling_frequency_hz=np.nan,
            bandwidth_low_hz=np.nan,bandwidth_high_hz=np.nan,aggregation_window_seconds=np.nan,
            output_interval_seconds=300,contract_status='no_adquisicion_real_no_espectro'))
    return pd.DataFrame(rows)
