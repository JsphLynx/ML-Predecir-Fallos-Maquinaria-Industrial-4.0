"""Simulador didáctico CSP. Todos los valores son sintéticos; no calibrado a ACB.
Ejecutable en Spyder (F5) o con Python. No requiere acceso a Internet.
"""
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def generate(seed=20261029, days=90):
    rng = np.random.default_rng(seed)
    out = ROOT / "datos"
    out.mkdir(exist_ok=True)
    n = days * 288
    times = pd.date_range("2025-01-01", periods=n, freq="5min", tz="UTC")
    step = np.arange(n)
    assets = []

    def add(aid, stage, family, kw, rpm, circuit, voltage=400):
        assets.append(dict(equipo_id=aid, etapa=stage, familia=family,
                           potencia_nominal_kw=kw, rpm_nominal=rpm,
                           presion_circuito_nominal_bar=circuit,
                           tension_v=voltage, vida_demo_h=float(rng.uniform(250, 550))))

    for k in (1, 2):
        add(f"COL{k}", "colada", "accionamiento", 160, 750, 0)
        add(f"HT{k}", "horno_tunel", "rodillos", 90, 750, 0)
    add("TIJ", "corte", "hidraulico", 110, 1500, 180)
    add("DESC", "descascarillado", "bomba", 800, 1500, 180, 6600)
    for k in range(1, 8):
        add(f"F{k}", "laminacion", "caja", 4500, 200 + 50*k, 210, 6600)
    add("HID", "auxiliares", "hidraulico", 220, 1500, 210)
    add("LUB", "auxiliares", "lubricacion", 55, 1450, 5)
    add("COOL", "enfriamiento", "bomba", 400, 1480, 12, 6600)
    add("ROT", "mesa_salida", "rodillos", 180, 900, 0)
    for k in (1, 2):
        add(f"BOB{k}", "bobinado", "bobinadora", 1500, 420, 160, 6600)
    a = pd.DataFrame(assets)
    m = len(a)
    # Schedules are proposed simulation assumptions, not company schedules.
    minute = step % 288
    planned = ((step // 288) % 7 == 6) & (minute < 72)
    wait = (minute >= 48) & (minute < 60)
    base_run = ~(planned | wait)
    base_run[:12] = False
    grade_block = step // 144
    grades = rng.choice(["DEMO_LC", "DEMO_HSLA", "DEMO_B"],
                        size=int(grade_block.max())+1, p=[.60, .28, .12])
    target_choices = rng.choice([1.8, 2.5, 3., 4., 6., 8.], size=len(grades))
    widths = rng.choice([1000., 1200., 1400.], size=len(grades))
    strength = np.select([grades[grade_block] == "DEMO_HSLA", grades[grade_block] == "DEMO_B"], [1.2, 1.12], 1.)
    ambient = 15 + 5*np.sin(2*np.pi*step/288) + rng.normal(0, .6, n)
    demand = np.clip((.52 + .12*np.log(60/target_choices[grade_block])) * strength, .4, 1.1)
    damage = rng.uniform(.02, .16, m)
    repair_until = np.zeros(m, dtype=int)
    age = np.zeros(m)
    temperature = np.full(m, 25.)
    vib_noise = np.zeros(m)
    modes = {"accionamiento": "rodamiento", "rodillos": "rodamiento", "hidraulico": "fuga_hidraulica",
             "bomba": "bomba_degradada", "caja": "rodamiento_transmision",
             "lubricacion": "lubricacion_insuficiente", "bobinadora": "accionamiento_bobinadora"}
    # Keep unobservable simulator internals separate from sensor records.
    truth_damage = np.zeros((n, m), dtype=np.float32)
    active = np.zeros((n, m), dtype=bool)
    stopped = np.zeros((n, m), dtype=bool)
    sensor = np.zeros((n, m, 8), dtype=np.float32)
    line_state = []
    events, maintenance = [], []
    restart_count = 0
    previous_running = False
    for t in range(n):
        # Planned replacements on three dates, inside a planned daily waiting window.
        if t // 288 in (20, 48, 76) and t % 288 == 50:
            eligible = np.where((damage > .45) & (repair_until <= t))[0]
            for j in eligible[:3]:
                repair_until[j] = t+6
                damage[j] = rng.uniform(.03, .12)
                maintenance.append(dict(mantenimiento_id=f"M{len(maintenance)+1:04d}",
                    equipo_id=a.equipo_id[j], evento_id="", tipo="preventivo",
                    inicio_idx=t, fin_idx=t+6, coste_eur=int(rng.integers(400, 1600))))
        for j in range(m):
            if repair_until[j] == t and t > 0:
                damage[j] = rng.uniform(.02, .10)
                age[j] = 0
        available = repair_until <= t
        running = bool(base_run[t] and available.all())
        if running and not previous_running:
            restart_count = 3
        loading = demand[t] * (.65 if restart_count > 0 else 1.) if running else .03
        if running:
            age += 5/60
            damage += (5/60/a.vida_demo_h.to_numpy()) * loading**1.6 * rng.lognormal(0, .20, m)
            shock = rng.random(m) < .000025
            failed = np.where(available & ((damage >= 1) | shock))[0]
            if len(failed):
                # One root incident per timestamp; conservative global line interruption.
                j = int(failed[0])
                duration = int(rng.integers(12, 49))
                repair_until[j] = t+duration
                eid = f"E{len(events)+1:04d}"
                events.append(dict(evento_id=eid, equipo_id=a.equipo_id[j], inicio_idx=t,
                    fin_idx=t+duration, modo_fallo="subito" if shock[j] else modes[a.familia[j]],
                    origen="SINTETICO"))
                maintenance.append(dict(mantenimiento_id=f"M{len(maintenance)+1:04d}",
                    equipo_id=a.equipo_id[j], evento_id=eid, tipo="correctivo",
                    inicio_idx=t, fin_idx=t+duration, coste_eur=int(rng.integers(800, 6000))))
                available[j] = False
                running, loading = False, .03
        if not available.all():
            state = "parada_mantenimiento"
        elif planned[t]:
            state = "parada_programada"
        elif t < 12:
            state = "preparacion"
        elif wait[t]:
            state = "espera_producto"
        elif restart_count:
            state = "arranque"
        else:
            state = "produccion"
        line_state.append(state)
        active[t] = running & available
        stopped[t] = ~available
        truth_damage[t] = damage
        # Current product changes and startup transients can resemble faults.
        transient = 1. if (restart_count > 0 and running) else 0.
        motor_load = loading * rng.uniform(.94, 1.06, m)
        motor_load *= available
        rpm = a.rpm_nominal.to_numpy() * (.70 + .25*loading) if running else np.zeros(m)
        rpm *= available
        torque = (a.potencia_nominal_kw.to_numpy()*9550/a.rpm_nominal.to_numpy()) * motor_load * (1+.12*damage)
        mech_kw = torque*rpm/9550
        efficiency = .94-.09*damage
        kw = mech_kw/efficiency + 0.005*a.potencia_nominal_kw.to_numpy()*available
        amps = kw*1000/(np.sqrt(3)*a.tension_v.to_numpy()*.88)
        target_temp = ambient[t]+12+36*motor_load+25*damage**2*motor_load
        temperature = .96*temperature + .04*target_temp + rng.normal(0, .18, m)
        vib_noise = .85*vib_noise + rng.normal(0, .22, m)
        vibration = np.maximum(.03, .35+1.2*motor_load+3.2*damage**2*motor_load+transient*.9+vib_noise)
        pressure = a.presion_circuito_nominal_bar.to_numpy()*(1-.22*damage**2)*available
        pressure *= (1 if running else .25)
        pressure *= rng.normal(1,.012,m)
        sensor[t] = np.column_stack([rpm, torque, kw, amps, temperature, vibration, pressure, age])
        if restart_count > 0 and running:
            restart_count -= 1
        previous_running = running

    # The entire line is intentionally treated as a coupled availability island.
    # Future work: separate casting strands and explicit thermal buffers.
    line = pd.DataFrame(dict(timestamp=times, estado_linea=line_state,
                             grado_programado=grades[grade_block],
                             espesor_objetivo_mm=target_choices[grade_block],
                             ancho_objetivo_mm=widths[grade_block],
                             ambiente_c=ambient.round(3)))
    for frame in (pd.DataFrame(events), pd.DataFrame(maintenance)):
        for c in ("inicio_idx", "fin_idx"):
            frame[c.replace("_idx", "")] = times[0] + pd.to_timedelta(frame[c]*5, unit="min")
        if "mantenimiento_id" in frame:
            maint = frame
        else:
            ev = frame
    cols = ["rpm", "par_nm", "potencia_kw", "corriente_a", "temperatura_equipo_c",
            "vibracion_rms_mm_s", "presion_circuito_bar", "horas_desde_intervencion"]
    telemetry = pd.DataFrame(sensor.reshape(-1, 8).astype(float), columns=cols)
    telemetry.insert(0, "equipo_id", np.tile(a.equipo_id, n))
    telemetry.insert(0, "timestamp", np.repeat(times, m))
    telemetry["equipo_disponible"] = (~stopped).ravel().astype(int)
    telemetry["en_marcha"] = active.ravel().astype(int)
    telemetry["presion_circuito_bar"] = telemetry.presion_circuito_bar.mask(np.tile(a.presion_circuito_nominal_bar.eq(0), n))
    # Two sensor defects per asset, plus independent missing observations.
    defects=[]
    for j in range(m):
        for kind in ("perdida_comunicacion", "deriva_sensor"):
            start=int(rng.integers(500,n-150)); end=start+int(rng.integers(24,100))
            column="vibracion_rms_mm_s" if kind=="perdida_comunicacion" else "temperatura_equipo_c"
            rows=np.arange(start,end)*m+j
            if kind=="perdida_comunicacion":
                telemetry.loc[rows,column]=np.nan
            else:
                telemetry.loc[rows,column]+=np.linspace(0,12,len(rows))
            defects.append(dict(equipo_id=a.equipo_id[j], inicio=times[start], fin=times[end],
                                variable=column, tipo=kind))
    for col in cols[:7]:
        telemetry.loc[rng.random(len(telemetry))<.004,col]=np.nan
    # Labels: future event strictly after t, full horizon observed, no intervention
    # before the endpoint. Never label terminal or maintenance-censored rows as zero.
    targets = telemetry[["timestamp","equipo_id"]].copy()
    for h in (1,4,24):
        y=np.full((n,m),np.nan)
        for j,aid in enumerate(a.equipo_id):
            starts=ev.loc[ev.equipo_id==aid,"inicio_idx"].to_numpy()
            pm=maint.loc[(maint.equipo_id==aid)&(maint.tipo=="preventivo"),"inicio_idx"].to_numpy()
            ends=step+h*12
            future_fail=np.searchsorted(starts,ends,side="right")-np.searchsorted(starts,step,side="right")
            future_pm=np.searchsorted(pm,ends,side="right")-np.searchsorted(pm,step,side="right")
            eligible=active[:,j] & (ends<n) & (future_pm==0)
            y[eligible,j]=(future_fail[eligible]>0).astype(int)
        targets[f"fallo_proximas_{h}h"] = pd.array(y.ravel(),dtype="Int8")
    split=np.where(step<54*288,"train",np.where(step<72*288,"validacion","test"))
    # 24 h purge before boundaries; keep all simultaneous assets in same partition.
    for boundary in (54*288,72*288):
        split[(step>=boundary-288)&(step<boundary)]="purga"
    targets["particion"]=np.repeat(split,m)
    truth=targets[["timestamp","equipo_id"]].copy()
    truth["degradacion_latente"]=truth_damage.ravel()

    # Coil and stage tables: material geometry obeys mass/volume conservation.
    # Times below are material-head milestones, not full residence intervals.
    coils, route, pass_rows, profiles = [], [], [], []
    cid=0
    for t in range(12,n-3,2):
        if t<10 or not active[t-8:t+3].all():
            continue
        cid+=1; coil=f"B{cid:05d}"
        strand=1+cid%2; coiler=1+cid%2
        b=grade_block[t]; width=float(widths[b]); target=float(target_choices[b])
        mass=float(rng.uniform(19000,28000)); hin=60.
        length=mass/(7850*(width/1000)*(hin/1000))
        loss=float(rng.uniform(.007,.018)); out_mass=mass*(1-loss)
        out_h=target*(1+rng.normal(0,.004))
        out_length=out_mass/(7850*(width/1000)*(out_h/1000))
        heat=f"H{b:04d}_{(t%144)//8:02d}"
        mill_ts=times[t]
        casting=mill_ts-pd.Timedelta(minutes=40)
        coil_end=mill_ts+pd.Timedelta(minutes=5)
        inlet_temp=float(rng.normal(1120,12))
        finish_temp=float(rng.normal(880,12))
        coil_temp=float(rng.normal(610,18))
        coils.append(dict(bobina_id=coil,colada_id=heat,linea_colada=f"COL{strand}",
            horno_id=f"HT{strand}",bobinadora_id=f"BOB{coiler}",grado_demo=grades[b],
            inicio_colada=casting,entrada_tren=mill_ts,fin_bobinado=coil_end,
            ancho_mm=width,espesor_planchon_mm=hin,espesor_objetivo_mm=target,
            espesor_final_mm=out_h,masa_planchon_kg=mass,masa_bobina_kg=out_mass,
            perdida_masa_kg=mass-out_mass,longitud_planchon_m=length,longitud_banda_m=out_length,
            temperatura_entrada_c=inlet_temp,temperatura_salida_c=finish_temp,
            temperatura_bobinado_c=coil_temp,origen="SINTETICO"))
        stages=[(f"COL{strand}",-40),(f"HT{strand}",-25),("DESC",-1)]+[(f"F{k}",(k-1)*.1) for k in range(1,8)]+[("COOL",.8),(f"BOB{coiler}",1.2)]
        for order,(aid,offset) in enumerate(stages,1):
            route.append(dict(bobina_id=coil,orden=order,equipo_id=aid,
                              paso_cabeza=mill_ts+pd.Timedelta(minutes=offset)))
        hs=np.geomspace(hin,out_h,8)
        exit_speed=out_length/180
        flux=(width/1000)*(out_h/1000)*exit_speed
        for k in range(1,8):
            j=int(a.index[a.equipo_id==f"F{k}"][0]); d=float(truth_damage[t,j])
            contact=np.sqrt(.35*((hs[k-1]-hs[k])/1000))
            flow_stress=120e6*strength[t]*(1+.04*k)
            force=(width/1000)*contact*flow_stress*(1+.06*d)
            torque=force*contact/2
            speed=flux/((width/1000)*(hs[k]/1000))
            rpm=speed/(np.pi*.7)*60
            power=torque*(2*np.pi*rpm/60)/1000
            pass_rows.append(dict(bobina_id=coil,equipo_id=f"F{k}",caja=k,
                espesor_entrada_mm=hs[k-1],espesor_salida_mm=hs[k],ancho_mm=width,
                reduccion_fraccion=1-hs[k]/hs[k-1],velocidad_banda_m_s=speed,
                caudal_volumetrico_m3_s=flux,fuerza_mn=force/1e6,par_estimado_nm=torque,
                potencia_mecanica_estimada_kw=power,
                temperatura_banda_c=inlet_temp+(finish_temp-inlet_temp)*k/7))
        for sec in range(0,181,5):
            frac=sec/180
            factor=.45+.55*min(1,frac/.12,(1-frac)/.10)
            phase="enhebrado" if sec<25 else ("salida_cola" if sec>160 else "regimen")
            profiles.append(dict(bobina_id=coil,timestamp=mill_ts+pd.Timedelta(seconds=36+sec),
                fase=phase,velocidad_salida_m_s=exit_speed*factor,
                factor_fuerza=1+.15*np.exp(-sec/12)+rng.normal(0,.015)))
    coils=pd.DataFrame(coils); route=pd.DataFrame(route); passes=pd.DataFrame(pass_rows)
    # Profiles illustrate speed transients; normalise their integral to the coil length.
    profiles=pd.DataFrame(profiles)
    length_map=coils.set_index("bobina_id").longitud_banda_m
    for coil,g in profiles.groupby("bobina_id",sort=False):
        actual=np.trapezoid(g.velocidad_salida_m_s.to_numpy(),dx=5)
        goal=float(length_map[coil])
        profiles.loc[g.index,"velocidad_salida_m_s"]*=goal/actual
    heats=coils.groupby("colada_id").agg(grado_demo=("grado_demo","first"),
          inicio=("inicio_colada","min"),masa_asignada_kg=("masa_planchon_kg","sum")).reset_index()
    heats["carbono_pct"]=[float(rng.uniform(.035,.07) if g=="DEMO_LC" else rng.uniform(.08,.16)) for g in heats.grado_demo]
    heats["manganeso_pct"]=[float(rng.uniform(.3,.6) if g=="DEMO_LC" else rng.uniform(.9,1.4)) for g in heats.grado_demo]
    # A heat is only the assigned slab batch within the simulated scope, not furnace capacity.
    # Process-level proxy signals at 5 min; not PLC tags or a thermodynamic solver.
    process_rng=np.random.default_rng(seed+1)
    process=pd.DataFrame({"timestamp":times})
    operating=active.all(axis=1)
    for k in (1,2):
        j=int(a.index[a.equipo_id==f"COL{k}"][0])
        process[f"col{k}_velocidad_m_min"]=np.where(operating,2.1+process_rng.normal(0,.08,n),0.)
        process[f"col{k}_nivel_molde_mm"]=np.where(operating,65+process_rng.normal(0,1.5,n)*(1+truth_damage[:,j]),np.nan)
        process[f"col{k}_temperatura_artesa_c"]=np.where(operating,1550+process_rng.normal(0,6,n),np.nan)
        for zone,nominal in ((1,1135),(2,1125),(3,1120)):
            process[f"ht{k}_zona{zone}_c"]=nominal+process_rng.normal(0,4,n)-8*(~operating)
    process["desc_presion_bar"]=sensor[:,int(a.index[a.equipo_id=="DESC"][0]),6]
    process["temperatura_entrada_tren_c"]=np.where(operating,1120+process_rng.normal(0,12,n),np.nan)
    process["temperatura_salida_tren_c"]=np.where(operating,880+process_rng.normal(0,12,n),np.nan)
    process["enfriamiento_caudal_m3_h"]=np.where(operating,900*demand+process_rng.normal(0,12,n),0.)
    process["temperatura_bobinado_c"]=np.where(operating,610+process_rng.normal(0,18,n),np.nan)
    for k in (1,2):
        process[f"bob{k}_tension_banda_kn"]=np.where(operating,45*demand+process_rng.normal(0,2,n),0.)
    tables={"equipos":a.drop(columns="vida_demo_h"),"estado_linea":line,"proceso_linea":process,
            "telemetria":telemetry,"objetivos_ml":targets,"eventos_fallo":ev.drop(columns=["inicio_idx","fin_idx"]),
            "mantenimiento":maint.drop(columns=["inicio_idx","fin_idx"]),"bobinas":coils,
            "coladas":heats,"trazabilidad":route,"pasadas_laminacion":passes,
            "perfiles_bobina":profiles,"verdad_simulador":truth,"incidencias_sensor":pd.DataFrame(defects)}
    for name,df in tables.items():
        df.to_csv(out/f"{name}.csv.gz",index=False,float_format="%.6f",
                  compression={"method":"gzip","mtime":0})
    config=dict(seed=seed,days=days,step_minutes=5,start_utc=str(times[0]),
        end_exclusive_utc=str(times[-1]+pd.Timedelta(minutes=5)),
        synthetic=True,calibrated_to_ACB=False,version="1.0",
        asset_life_hours=dict(zip(a.equipo_id,a.vida_demo_h)),
        note="Parámetros y frecuencias de fallo son hipótesis didácticas, no estadísticas de ACB.")
    (ROOT/"configuracion.json").write_text(json.dumps(config,indent=2,ensure_ascii=False),encoding="utf-8")
    summary={name:{"filas":len(df),"columnas":len(df.columns)} for name,df in tables.items()}
    (ROOT/"resultados/resumen_generacion.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--seed",type=int,default=20261029)
    parser.add_argument("--days",type=int,default=90)
    args,_=parser.parse_known_args()
    if args.days < 80:
        raise ValueError("Esta configuración de particiones requiere al menos 80 días.")
    generate(args.seed,args.days)
