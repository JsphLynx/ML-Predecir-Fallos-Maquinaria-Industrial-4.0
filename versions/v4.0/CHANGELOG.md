# Historial

## 4.0.0 · 20/11/2026

- Segmentos contiguos en todos los estados; eliminación de coil_id y separación de velocidades.
- Modelo cuasiestático, transmisión, fuerza, par, potencia, eficiencia e intensidad trifásica.
- 26 señales; física limpia privada; parámetros de procedencia declarada.
- Dos configuraciones virtuales, historial de validez y reinicio de ventanas por dominio.
- Contrato de sensores explicita desconocidos de adquisición de alta frecuencia.
- Semillas, features, etiquetas, particiones, diccionario, SQL, protocolo y validaciones regenerados.
- Reproducción íntegra por SHA-256 y pruebas de sensibilidad/independencia instrumental.
- Sin entrenamiento de modelos; sin calibración industrial; integración PostgreSQL no ejecutada.

La v3.1 se conserva como línea base externa. Los arreglos de integración detectados durante construcción (posición de retorno del fixture al añadir verdad física) se resolvieron antes del cierre; no se ajustó el simulador por rendimiento predictivo.
