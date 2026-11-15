"""Comprobaciones de estructura, trazabilidad, física simplificada y objetivos."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]


def read(name):
    return pd.read_csv(ROOT/"datos"/f"{name}.csv.gz")


def validate():
    a=read("equipos"); t=read("telemetria"); y=read("objetivos_ml")
    e=read("eventos_fallo"); m=read("mantenimiento"); c=read("bobinas")
    h=read("coladas"); p=read("pasadas_laminacion"); r=read("trazabilidad")
    profiles=read("perfiles_bobina")
    checks={}
    checks["pk_telemetria"] = not t.duplicated(["timestamp","equipo_id"]).any()
    checks["pk_bobinas"] = c.bobina_id.is_unique
    checks["pk_equipos"] = a.equipo_id.is_unique
    checks["claves_objetivos"] = t[["timestamp","equipo_id"]].equals(y[["timestamp","equipo_id"]])
    checks["fk_equipos"] = all(set(df.equipo_id)<=set(a.equipo_id) for df in (t,e,m,p,r))
    checks["fk_coladas"] = set(c.colada_id)<=set(h.colada_id)
    checks["fk_bobinas"] = all(set(df.bobina_id)<=set(c.bobina_id) for df in (p,r,profiles))
    checks["siete_pasadas"] = bool(p.groupby("bobina_id").size().eq(7).all())
    checks["doce_hitos"] = bool(r.groupby("bobina_id").size().eq(12).all())
    checks["reduccion_espesor"] = bool((p.espesor_entrada_mm>p.espesor_salida_mm).all())
    checks["continuidad_cajas"] = bool(np.allclose(p.loc[p.caja>1,"espesor_entrada_mm"],p.groupby("bobina_id").espesor_salida_mm.shift().loc[p.caja>1]))
    checks["balance_masa"] = bool(np.allclose(c.masa_planchon_kg,c.masa_bobina_kg+c.perdida_masa_kg,atol=1e-4))
    mass_est=c.longitud_banda_m*c.ancho_mm/1000*c.espesor_final_mm/1000*7850
    checks["masa_geometria"] = bool(np.allclose(c.masa_bobina_kg,mass_est,rtol=1e-5))
    flux=p.ancho_mm/1000*p.espesor_salida_mm/1000*p.velocidad_banda_m_s
    checks["conservacion_caudal"] = bool(np.allclose(flux,p.caudal_volumetrico_m3_s,atol=1e-6))
    integrals=profiles.groupby("bobina_id",sort=False).velocidad_salida_m_s.apply(lambda s: np.trapezoid(s.to_numpy(),dx=5))
    checks["integral_perfil_longitud"] = bool(np.allclose(integrals,c.set_index("bobina_id").loc[integrals.index,"longitud_banda_m"],atol=.001))
    checks["hitos_ordenados"] = bool((pd.to_datetime(r.paso_cabeza,utc=True).groupby(r.bobina_id).diff().dropna()>=pd.Timedelta(0)).all())
    checks["tiempos_mantenimiento"] = bool((pd.to_datetime(m.fin)>pd.to_datetime(m.inicio)).all())
    checks["fk_averia_correctivo"] = set(m.loc[m.tipo=="correctivo","evento_id"])==set(e.evento_id)
    checks["no_objetivo_fuera_marcha"] = bool(y.loc[t.en_marcha.eq(0),[f"fallo_proximas_{h}h" for h in (1,4,24)]].isna().all().all())
    dates=pd.to_datetime(y.timestamp,utc=True)
    end=pd.Timestamp(json.loads((ROOT/"configuracion.json").read_text())["end_exclusive_utc"])
    checks["censura_final_24h"] = bool(y.loc[dates>=end-pd.Timedelta(hours=24),"fallo_proximas_24h"].isna().all())
    checks["purga_train"] = bool((dates[y.particion.eq("train")].max()+pd.Timedelta(hours=24))<dates[y.particion.eq("validacion")].min())
    checks["purga_validacion"] = bool((dates[y.particion.eq("validacion")].max()+pd.Timedelta(hours=24))<dates[y.particion.eq("test")].min())
    # Independent reconstruction of label windows on random rows, including NA.
    rng=np.random.default_rng(73); mismatches=0
    for idx in rng.choice(len(y),3000,replace=False):
        row=y.iloc[idx]; ts=dates.iloc[idx]; aid=row.equipo_id
        failures=pd.to_datetime(e.loc[e.equipo_id==aid,"inicio"],utc=True)
        pm=pd.to_datetime(m.loc[(m.equipo_id==aid)&m.tipo.eq("preventivo"),"inicio"],utc=True)
        for hours in (1,4,24):
            stop=ts+pd.Timedelta(hours=hours)
            eligible=t.en_marcha.iloc[idx]==1 and stop<end and not ((pm>ts)&(pm<=stop)).any()
            expected=int(((failures>ts)&(failures<=stop)).any()) if eligible else np.nan
            value=row[f"fallo_proximas_{hours}h"]
            mismatches+=not ((pd.isna(value) and pd.isna(expected)) or value==expected)
    checks["etiquetas_recalculadas_9000"]=mismatches==0
    stats={"comprobaciones":{k:bool(v) for k,v in checks.items()},
           "todas_correctas":all(checks.values()),"fallos":len(e),"equipos":len(a),"bobinas":len(c),
           "telemetria_filas":len(t),"fallos_por_modo":e.modo_fallo.value_counts().to_dict(),
           "prevalencia_4h_por_particion":y.groupby("particion").fallo_proximas_4h.mean().to_dict(),
           "ausentes_por_variable":t.isna().mean().to_dict(),
           "nota":"Los controles verifican el simulador, no validan su equivalencia con ACB."}
    (ROOT/"resultados/validacion.json").write_text(json.dumps(stats,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(stats,indent=2,ensure_ascii=False))
    assert all(checks.values()), "Existen comprobaciones fallidas: revisar validacion.json"


if __name__=="__main__":
    validate()
