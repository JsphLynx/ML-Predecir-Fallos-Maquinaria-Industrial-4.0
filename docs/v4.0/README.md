# Versión 4.0 · Motor y rodamientos

**22/11/2026 · [Auditoría cerrada y descargas de la revisión A](revision-a/).** Esta es la revisión preparada para el entrenamiento sintético. La documentación que sigue corresponde a la entrega original.

**Originales v4.0 incorporados.** Código, documentación y ejemplos en [versions/v4.0](../../versions/v4.0/). Los datos completos se distribuyen en dos ZIP. [Estado y alcance de la publicación](PUBLICACION.md).

[Lectura para reclutadores](PORTFOLIO.md) · [Arquitectura y contrato](ARQUITECTURA.md) · [Validación documentada](VALIDACION.md) · [Auditoría posterior](AUDITORIA_POSTERIOR.md) · [Distribución y trazabilidad](PUBLICACION.md)

## Qué cambia

La v4.0 sustituye las heurísticas de velocidad y corriente por un modelo mecánico mínimo con relaciones explícitas entre geometría, fuerza, par, velocidad, potencia y corriente. Mantiene una caja lógica con un motor y apoyos DE/NDE. No representa las siete cajas reales de Sestao.

| Elemento | v4.0 |
|---|---|
| Realizaciones | 16 mundos alternativos de 365 días |
| Telemetría | 1.681.920 observaciones; cada 5 minutos |
| Decisiones | 560.640; cada 15 minutos |
| Señales | 26 |
| Predictores permitidos | 187 numéricos y 4 categóricos |
| Objetivo | Fallo funcional en las siguientes 24 horas, con censura |
| Eventos | 814 fallos simulados |
| Configuración | Dos dominios virtuales con validez temporal |
| Entrenamiento de XGBoost/Isolation Forest | Pendiente |

Fuente: *Informe_Mejora_Dataset_v4_0.pdf*, páginas 1–7, leído el 21/11/2026. No confundir estos recuentos documentados con pruebas nuevas ejecutadas durante esta incorporación.

## Mejoras trazables

- `production_segment_id` identifica bloques contiguos de receta/estado/configuración. No se presenta como bobina física.
- Motor, cilindros y banda tienen velocidades distintas y unidades explícitas.
- Fuerza, par, potencia, eficiencia, tensión y corriente se relacionan mediante un modelo cuasiestático.
- Los parámetros sin evidencia industrial se declaran supuestos. El fabricante/modelo del motor real permanece desconocido.
- La verdad física limpia se separa de las observaciones con defectos y de los predictores.
- Las ventanas se reinician al cambiar de configuración.
- El contrato de vibración declara frecuencia, banda, ventana, eje y montaje desconocidos/no especificados.

## Continuidad

Conservar v1, v2, v3 y v3.1. La nueva versión modifica mecanismos, variables y semillas; no concatenar sus filas ni interpretar las tasas de fallo como una mejora de fiabilidad real. La auditoría posterior recomienda mantener v4.0 como base y ensayar las ampliaciones por separado.

Los informes y paquetes originales están inventariados en [PUBLICACION.md](PUBLICACION.md). No se publican enlaces privados como sustituto de descargas accesibles a reclutadores.
