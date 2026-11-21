# Modelo físico v4.0.0

Una caja equivalente con un accionamiento lógico para dos cilindros. El catálogo NO representa las siete cajas reales ni una caja F4. `demo_position=4` es una etiqueta didáctica sin efecto en el cálculo. No se generan bobinas físicas: `production_segment_id` identifica un intervalo contiguo de receta/estado/configuración. En las paradas y tras una interrupción empieza otro segmento. Su fin es retrospectivo y no entra en predictores.

## Ecuaciones y unidades

- Reducción `r`: 0,18–0,32. `h_in = h_out/(1-r)` en mm. Ancho constante; no ensanchamiento ni pérdidas de masa.
- `l = sqrt(R * (h_in-h_out)/1000)` en metros; R=0,35 m.
- `sigma = 130e6 * factor_grado * exp(-0.003*(T-900))` en Pa. **Ley elegida para demostración, no ajuste a Nucor ni Sestao.**
- `F = sigma * (ancho_mm/1000) * l * 1.15` en N.
- `tau_roll = 2 * F * l * 0.5` en Nm: par equivalente de dos cilindros; no par individual de cada cilindro.
- `v_out = 2*pi*R*rpm_roll/60*(1+slip)`; slip=0,03. `rpm_motor = gear_ratio*rpm_roll`.
- `h_in*v_in = h_out*v_out`: continuidad con ancho y densidad constantes. La densidad de 7.850 kg/m³ está documentada para extensión a masa, pero no se calcula masa de bobina ni caudal másico en esta versión.
- `P_motor = tau_roll*omega_roll/eta_trans + P_idle` en W. Auxiliares equivalentes activos: 60 kW. No representan un motor auxiliar real.
- `tau_motor = P_motor/omega_motor`; par cero con motor parado.
- `eta_effective = eta_config*(1-0.05*min(pre_motor,3))`; `pre_motor` procede del estado latente. Es una ley de pérdida supuesta, no curva OEM.
- `P_electric = P_motor/eta_effective`; `I = P_electric/(sqrt(3)*U_LL*PF)`. Hipótesis: alimentación trifásica equilibrada, RMS, U_LL=3.300 V y PF=0,90 constantes. No estima armónicos ni convertidor.
- `load_ratio = P_motor / 2.000 kW`. No se recorta artificialmente a 1: sobrecarga es posible en la simulación. No es porcentaje de par nominal.

En archivos se usan kN, kNm y kW; las conversiones están explícitas en código. Los resultados limpios y eficiencia efectiva van a `sim_truth/fisica`, prohibidos como predictores. La telemetría recibe ruido, ganancia, deriva, congelación, pérdidas y latencia. No tiene por qué satisfacer exactamente las identidades: sí las satisface la referencia limpia dentro de la tolerancia numérica.

## Alcance temporal y contexto

Se mantiene paso interno de 5 min. Cada fila es un estado cuasiestático: no es una onda ni una integral exacta de un ciclo. No se modelan mordida, tensión entre cajas, elasticidad de bastidor, perfiles térmicos, fuerzas laterales ni resonancias. Arranque/sin carga/desaceleración usan consignas de cilindro de 45/90/35 rpm; no modelan rampas subsegundo.

Dos dominios de configuración: al inicio y desde el día 183. Cambian relación de transmisión (6 a 5,7), eficiencia nominal (0,94 a 0,96), identificación de control/sensores y ganancia común (1 a 1,02). Es un cambio experimental virtual instantáneo; no acredita una modernización real ni simula su obra/parada. El daño NO se reinicia por este cambio. Las intervenciones de mantenimiento conservan su calendario y lógica propios.

Las ventanas de señales se reinician por dominio para no mezclar instrumentos. Los metadatos de configuración se conocen en su inicio. Catálogo `valid_to` y fin de segmento son retrospectivos: no usarlos como entradas.

La temperatura de banda no se traslada a temperatura de apoyo/devanado. Fuera de laminación, espesores y temperatura de banda son nulos; fuerzas y velocidad de banda son cero en referencia limpia. Las señales rotativas pueden seguir activas sin banda.

## Vibración

Descriptores RMS de velocidad/aceleración y curtosis de Pearson generados directamente. Frecuencia original, ancho de banda, ventana de adquisición, eje y montaje son desconocidos/no especificados. 300 segundos es cadencia de salida y NO frecuencia de adquisición. No se generan espectros, BPFO/BPFI ni ondas ficticias de alta frecuencia.

## Fuentes y límites

El informe adjunto, páginas 10–14, motiva cada mejora. Nucor sirve de referencia de variables de proceso; TCM corresponde a laminación en frío; Paderborn/IMS son bancos de ensayo. Ningún valor externo se ha mezclado con el dataset, no se han unido fábricas por fecha y no se han transferido etiquetas. Los parámetros numéricos físicos son supuestos. El fabricante/modelo real del motor permanece desconocido.
