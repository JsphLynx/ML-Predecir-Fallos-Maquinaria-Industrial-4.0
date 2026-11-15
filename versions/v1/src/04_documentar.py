"""Genera diccionario, fuentes y resumen legible a partir de la entrega validada."""
from pathlib import Path
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DESCRIPTIONS={
"timestamp":"Instante de observación; UTC.","equipo_id":"Identificador sintético del subsistema equivalente.",
"etapa":"Etapa del proceso representada.","familia":"Familia funcional del equipo equivalente.",
"potencia_nominal_kw":"Potencia nominal supuesta del accionamiento equivalente; no dato de fabricante.",
"rpm_nominal":"Velocidad nominal supuesta del accionamiento.",
"presion_circuito_nominal_bar":"Referencia supuesta del circuito; cero significa no aplicable.",
"tension_v":"Tensión trifásica supuesta para calcular corriente equivalente.",
"estado_linea":"preparacion, arranque, produccion, parada_programada, espera_producto o parada_mantenimiento.",
"grado_programado":"Familia sintética del programa vigente; DEMO_LC, DEMO_HSLA o DEMO_B.",
"grado_demo":"Familia ilustrativa de acero; no grado normalizado.",
"espesor_objetivo_mm":"Espesor previsto por el programa de fabricación.",
"ancho_objetivo_mm":"Anchura prevista por el programa.","ambiente_c":"Temperatura ambiental sintética con ciclo diario y ruido.",
"rpm":"Velocidad del accionamiento equivalente; cero en parada, vacío si pérdida de dato.",
"par_nm":"Par del accionamiento equivalente derivado de carga y desgaste.",
"potencia_kw":"Potencia eléctrica equivalente derivada de par, rpm, eficiencia y consumo auxiliar.",
"corriente_a":"Corriente equivalente calculada con factor de potencia supuesto 0,88.",
"temperatura_equipo_c":"Temperatura local con inercia; incluye posible deriva de sensor.",
"vibracion_rms_mm_s":"RMS de vibración agregada sintética; no forma de onda ni espectro.",
"presion_circuito_bar":"Presión equivalente; vacío por no aplicabilidad o pérdida de dato.",
"horas_desde_intervencion":"Horas de marcha desde intervención finalizada; al comienzo, desde inicio del escenario.",
"equipo_disponible":"1 si no está en intervención, 0 si está indisponible.",
"en_marcha":"1 si marcha la isla de producción y está disponible el equipo; 0 en otro caso.",
"fallo_proximas_1h":"1 si inicia fallo del mismo equipo en (t,t+1h], 0 si no, vacío si censurado/no elegible.",
"fallo_proximas_4h":"1 si inicia fallo del mismo equipo en (t,t+4h], 0 si no, vacío si censurado/no elegible.",
"fallo_proximas_24h":"1 si inicia fallo del mismo equipo en (t,t+24h], 0 si no, vacío si censurado/no elegible.",
"particion":"train, validacion, test o purga; metadato de evaluación, nunca predictor.",
"evento_id":"Clave de avería; vacío en intervención preventiva sin avería.",
"modo_fallo":"Modo sintético atribuido a la avería; no diagnóstico basado en inspección real.",
"origen":"SINTETICO, identifica generación artificial.","inicio":"Inicio de suceso o primer material asignado al lote.",
"fin":"Fin exclusivo de intervención o incidencia; puede rebasar el periodo observado.",
"mantenimiento_id":"Identificador único de intervención.","tipo":"Tipo de intervención (preventivo/correctivo) o incidencia de sensor, según tabla.",
"coste_eur":"Coste hipotético final de intervención; sin datos de empresa.",
"bobina_id":"Identificador de bobina sintética completa.","colada_id":"Identificador de lote de material asignado; no carga de horno real.",
"linea_colada":"COL1 o COL2 asignada a la ruta de la bobina.","horno_id":"HT1 o HT2 asignado a la ruta.",
"bobinadora_id":"BOB1 o BOB2 asignada a la ruta de la bobina.","inicio_colada":"Hito ilustrativo de colada del material.",
"entrada_tren":"Instante de entrada de cabeza en F1.","fin_bobinado":"Fin ilustrativo de bobinado/extracción.",
"ancho_mm":"Anchura constante en el modelo; no se calcula ensanchamiento.",
"espesor_planchon_mm":"Espesor del planchón antes de reducción, supuesto 60 mm.",
"espesor_final_mm":"Espesor final sintético con variación respecto al objetivo; disponible al final.",
"masa_planchon_kg":"Masa inicial de planchón sintético.","masa_bobina_kg":"Masa final después de pérdidas sintéticas.",
"perdida_masa_kg":"Diferencia entre masa inicial y masa final; 0,7–1,8 % por hipótesis.",
"longitud_planchon_m":"Longitud derivada de masa, densidad y sección inicial.",
"longitud_banda_m":"Longitud derivada de masa, densidad y sección final.",
"temperatura_entrada_c":"Temperatura sintética de banda en entrada del tren, por bobina.",
"temperatura_salida_c":"Temperatura sintética de banda al salir del tren, por bobina.",
"temperatura_bobinado_c":"Temperatura sintética de bobinado; por bobina o instante según tabla.",
"masa_asignada_kg":"Suma de masas iniciales de bobinas asignadas al lote; no capacidad de horno.",
"carbono_pct":"Contenido de carbono ilustrativo del lote, sin certificación de composición.",
"manganeso_pct":"Contenido de manganeso ilustrativo del lote.","orden":"Orden del hito en la ruta de la bobina.",
"paso_cabeza":"Instante ilustrativo de llegada de cabeza; no duración de ocupación.",
"caja":"Número de caja, 1 a 7.","espesor_entrada_mm":"Espesor de entrada de pasada.",
"espesor_salida_mm":"Espesor de salida de pasada.","reduccion_fraccion":"1 - espesor_salida / espesor_entrada.",
"velocidad_banda_m_s":"Velocidad de referencia por caja compatible con caudal volumétrico.",
"caudal_volumetrico_m3_s":"Sección de banda por velocidad; constante entre cajas por bobina.",
"fuerza_mn":"Fuerza de laminación simplificada calculada con contacto y resistencia supuesta.",
"par_estimado_nm":"Par mecánico de pasada; distinto del accionamiento agregado de telemetría.",
"potencia_mecanica_estimada_kw":"Potencia mecánica de pasada sin modelo de transmisión real.",
"temperatura_banda_c":"Temperatura interpolada entre entrada y salida por caja.",
"fase":"enhebrado, regimen o salida_cola del perfil de banda.",
"velocidad_salida_m_s":"Perfil cuya integral de 180 s reproduce la longitud de banda.",
"factor_fuerza":"Factor adimensional ilustrativo del transitorio; no fuerza medida.",
"degradacion_latente":"Desgaste interno del generador; umbral de fallo 1, EXCLUIR de predictores.",
"variable":"Sensor afectado por una incidencia inyectada; registro interno del generador.",
"desc_presion_bar":"Presión de descascarillado de la señal equivalente de DESC.",
"enfriamiento_caudal_m3_h":"Caudal ilustrativo de enfriamiento ligado a carga; no balance térmico.",
"temperatura_entrada_tren_c":"Temperatura de contexto de entrada; vacío sin material en marcha.",
"temperatura_salida_tren_c":"Temperatura de contexto de salida; vacío sin material en marcha."}
for k in (1,2):
    DESCRIPTIONS[f"col{k}_velocidad_m_min"]=f"Velocidad proxy de colada {k}; cero con isla detenida."
    DESCRIPTIONS[f"col{k}_nivel_molde_mm"]=f"Nivel proxy de molde {k} respecto a referencia arbitraria; no límite real."
    DESCRIPTIONS[f"col{k}_temperatura_artesa_c"]=f"Temperatura proxy de artesa de línea {k}."
    DESCRIPTIONS[f"bob{k}_tension_banda_kn"]=f"Tensión proxy de bobinadora {k}; sin simular ocupación individual."
    for z in (1,2,3):
        DESCRIPTIONS[f"ht{k}_zona{z}_c"]=f"Temperatura ilustrativa de zona {z} del horno {k}; no modelo térmico."


def unit(col):
    if col in ("timestamp","inicio","fin","entrada_tren","inicio_colada","fin_bobinado","paso_cabeza"):
        return "ISO 8601 UTC"
    suffix={"_m3_s":"m³/s","_m3_h":"m³/h","_m_min":"m/min","_m_s":"m/s","_mm_s":"mm/s",
            "_kw":"kW","_kn":"kN","_nm":"N·m","_mn":"MN","_bar":"bar","_kg":"kg",
            "_mm":"mm","_pct":"% masa","_eur":"EUR","_c":"°C","_a":"A","_v":"V","_m":"m"}
    for end,value in suffix.items():
        if col.endswith(end):return value
    if col in ("rpm","rpm_nominal"):return "rev/min"
    if col=="horas_desde_intervencion":return "h de marcha"
    return "adimensional/categoría"


def document():
    rows=[]
    for f in sorted((ROOT/"datos").glob("*.csv.gz")):
        name=f.name.removesuffix(".csv.gz")
        sample=pd.read_csv(f,nrows=200)
        for col in sample:
            assert col in DESCRIPTIONS, f"Falta descripción: {col}"
            role="Solo después del resultado; excluir del modelo inicial"
            if name in ("telemetria","estado_linea","proceso_linea","equipos"):
                role="Observable en t / catálogo; revisar pertinencia antes de incluir"
            if name=="objetivos_ml":role="Objetivo o partición; NO predictor"
            if name in ("verdad_simulador","incidencias_sensor"):role="Interno del simulador; NO predictor"
            if col in ("timestamp","equipo_id","bobina_id","colada_id"):role="Clave de unión; no predictor automático"
            rows.append(dict(tabla=name,variable=col,unidad=unit(col),
                             descripcion=DESCRIPTIONS[col],disponibilidad_y_uso=role,
                             procedencia="SINTETICO: hipótesis del generador; nunca medición de ACB"))
    pd.DataFrame(rows).to_csv(ROOT/"documentacion/diccionario.csv",index=False)
    sources=[
        ("S1","ArcelorMittal Europe — Sestao","https://flateurope.arcelormittal.com/ourmills/spain/sestao","Dos coladas, dos hornos túnel, un tren y dos bobinadoras"),
        ("S2","Declaración Ambiental Sestao 2023","https://spain.arcelormittal.com/wp-content/uploads/declaracion-ambiental-2023.pdf","Siete cajas y secuencia general; texto indexado, no inspección visual completa"),
        ("S3","SMS group — CSP Nexus","https://www.sms-group.com/pt-br/insights/all-insights/csp-nexus","Arquitectura CSP genérica; no consignas de ACB"),
        ("S4","SMS group — Hot strip mills","https://www.sms-group.com/plants/all-plants/hot-strip-mills-steel/","Función genérica de descascarillado, enfriamiento y bobinadoras")]
    df=pd.DataFrame(sources,columns=["id","fuente","url","alcance"])
    df["fecha_consulta"]="2026-10-29"
    df.to_csv(ROOT/"documentacion/fuentes.csv",index=False)
    checks=json.loads((ROOT/"resultados/validacion.json").read_text())
    model=json.loads((ROOT/"resultados/modelo_base.json").read_text())
    summary=json.loads((ROOT/"resultados/resumen_generacion.json").read_text())
    text=["# Resultado de la verificación — datos íntegramente sintéticos","",
          f"{len(checks['comprobaciones'])} comprobaciones superadas. No equivalen a validación de ingeniería.","",
          "| Tabla | Registros | Columnas |","|---|---:|---:|"]
    for name,s in summary.items():text.append(f"| {name} | {s['filas']:,} | {s['columnas']} |")
    text += ["","## Prueba de funcionamiento de ML, horizonte de cuatro horas","",
      f"Average precision: {model['test_average_precision']:.3f}; prevalencia de referencia: {model['test_prevalencia_base']:.3%}.",
      f"Precisión por muestra: {model['test_precision']:.1%}; recall por muestra: {model['test_recall']:.1%}.",
      f"Aviso previo en {model['eventos_con_aviso_4h']} de {model['eventos_evaluables_test']} eventos evaluables del test.",
      "","El modelo base tiene limitaciones claras y genera falsos avisos. No se ha optimizado para obtener cifras vistosas. Los eventos son pocos; no se ha estimado incertidumbre. Los resultados solo prueban una ejecución de extremo a extremo sobre las hipótesis de este simulador.",
      "","La evaluación usa tiempo posterior sobre los mismos equipos. Las filas próximas no son eventos independientes. No presentar estas métricas como resultados de una planta real."]
    (ROOT/"resultados/LEER_RESULTADOS.md").write_text("\n".join(text)+"\n",encoding="utf-8")
    print(f"Diccionario: {len(rows)} campos documentados.")


if __name__=="__main__":
    document()
