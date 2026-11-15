-- Escenario 100% sintético. DDL PostgreSQL; NO ejecutado contra servidor.

BEGIN;

CREATE SCHEMA IF NOT EXISTS acb_demo;

CREATE TABLE IF NOT EXISTS acb_demo.paradas_linea (
    "parada_id" TEXT,
    "inicio" TIMESTAMPTZ,
    "fin" TIMESTAMPTZ,
    "tipo" TEXT,
    "evento_id" TEXT,
    "equipo_causa" TEXT,
    PRIMARY KEY ("parada_id")
);

CREATE TABLE IF NOT EXISTS acb_demo.equipos (
    "equipo_id" TEXT,
    "tipo_equipo" TEXT,
    "posicion" BIGINT,
    "potencia_nominal_kw" BIGINT,
    "modos_admisibles" TEXT,
    "origen" TEXT,
    "inventario_real" BOOLEAN,
    PRIMARY KEY ("equipo_id")
);

CREATE TABLE IF NOT EXISTS acb_demo.bobinas (
    "bobina_id" BIGINT,
    "inicio" TIMESTAMPTZ,
    "grado_acero" TEXT,
    "espesor_objetivo_mm" DOUBLE PRECISION,
    "ancho_mm" DOUBLE PRECISION,
    "masa_objetivo_t" DOUBLE PRECISION,
    "longitud_objetivo_m" DOUBLE PRECISION,
    "pasos_objetivo" BIGINT,
    "pasos_procesados" BIGINT,
    "rama_colada" TEXT,
    "bobinadora_id" TEXT,
    "fin" TIMESTAMPTZ,
    "estado_resultado" TEXT,
    "masa_procesada_t" DOUBLE PRECISION,
    "espesor_medido_final_mm" DOUBLE PRECISION,
    "disponible_resultado_desde" TIMESTAMPTZ,
    PRIMARY KEY ("bobina_id")
);

CREATE TABLE IF NOT EXISTS acb_demo.fallos (
    "evento_id" TEXT,
    "equipo_id" TEXT,
    "inicio" TIMESTAMPTZ,
    "fin" TIMESTAMPTZ,
    "modo_fallo" TEXT,
    "tipo_inicio" TEXT,
    "diagnostico_disponible_desde" TIMESTAMPTZ,
    "duracion_h" DOUBLE PRECISION,
    "coste_reparacion_eur_simulado" DOUBLE PRECISION,
    PRIMARY KEY ("evento_id")
);

CREATE TABLE IF NOT EXISTS acb_demo.productos (
    "grado_acero" TEXT,
    "espesor_min_demo_mm" DOUBLE PRECISION,
    "factor_carga_demo" DOUBLE PRECISION,
    PRIMARY KEY ("grado_acero")
);

CREATE TABLE IF NOT EXISTS acb_demo.mantenimiento (
    "mantenimiento_id" TEXT,
    "equipo_id" TEXT,
    "inicio" TIMESTAMPTZ,
    "fin" TIMESTAMPTZ,
    "tipo" TEXT,
    "evento_id" TEXT,
    "conocido_desde" TIMESTAMPTZ,
    "coste_eur_simulado" DOUBLE PRECISION,
    PRIMARY KEY ("mantenimiento_id")
);

CREATE TABLE IF NOT EXISTS acb_demo.estado_linea (
    "timestamp" TIMESTAMPTZ,
    "estado_linea" BIGINT,
    "bobina_id" BIGINT,
    "espesor_objetivo_mm" DOUBLE PRECISION,
    "ancho_mm" DOUBLE PRECISION,
    "velocidad_salida_m_s" DOUBLE PRECISION,
    "flujo_masa_kg_s" DOUBLE PRECISION,
    PRIMARY KEY ("timestamp")
);

CREATE TABLE IF NOT EXISTS acb_demo.telemetria (
    "equipo_id" TEXT,
    "timestamp" TIMESTAMPTZ,
    "disponible_desde" TIMESTAMPTZ,
    "tipo_equipo" TEXT,
    "estado_equipo" BIGINT,
    "en_marcha" BOOLEAN,
    "bobina_id" BIGINT,
    "grado_acero" TEXT,
    "espesor_objetivo_mm" DOUBLE PRECISION,
    "ancho_mm" DOUBLE PRECISION,
    "carga_relativa" DOUBLE PRECISION,
    "horas_desde_mantenimiento" DOUBLE PRECISION,
    "temperatura_ambiente_c" DOUBLE PRECISION,
    "vibracion_rms_mm_s" DOUBLE PRECISION,
    "temperatura_rodamiento_c" DOUBLE PRECISION,
    "temperatura_motor_c" DOUBLE PRECISION,
    "temperatura_aceite_c" DOUBLE PRECISION,
    "presion_aceite_bar" DOUBLE PRECISION,
    "presion_hidraulica_bar" DOUBLE PRECISION,
    "caudal_refrigeracion_l_min" DOUBLE PRECISION,
    "corriente_motor_pct_nominal" DOUBLE PRECISION,
    "velocidad_motor_rpm" DOUBLE PRECISION,
    "potencia_kw" DOUBLE PRECISION,
    "fuerza_laminacion_mn" DOUBLE PRECISION,
    "espesor_entrada_caja_mm" DOUBLE PRECISION,
    "espesor_salida_caja_mm" DOUBLE PRECISION,
    "velocidad_entrada_caja_m_s" DOUBLE PRECISION,
    "velocidad_salida_caja_m_s" DOUBLE PRECISION,
    "temperatura_material_c" DOUBLE PRECISION,
    PRIMARY KEY ("equipo_id", "timestamp")
);

CREATE TABLE IF NOT EXISTS acb_demo.features (
    "equipo_id" TEXT,
    "timestamp" TIMESTAMPTZ,
    "disponible_desde" TIMESTAMPTZ,
    "tipo_equipo" TEXT,
    "en_marcha" BOOLEAN,
    "grado_acero" TEXT,
    "espesor_objetivo_mm" DOUBLE PRECISION,
    "ancho_mm" DOUBLE PRECISION,
    "carga_relativa" DOUBLE PRECISION,
    "horas_desde_mantenimiento" DOUBLE PRECISION,
    "temperatura_ambiente_c" DOUBLE PRECISION,
    "vibracion_rms_mm_s" DOUBLE PRECISION,
    "temperatura_rodamiento_c" DOUBLE PRECISION,
    "temperatura_motor_c" DOUBLE PRECISION,
    "temperatura_aceite_c" DOUBLE PRECISION,
    "presion_aceite_bar" DOUBLE PRECISION,
    "presion_hidraulica_bar" DOUBLE PRECISION,
    "caudal_refrigeracion_l_min" DOUBLE PRECISION,
    "corriente_motor_pct_nominal" DOUBLE PRECISION,
    "velocidad_motor_rpm" DOUBLE PRECISION,
    "potencia_kw" DOUBLE PRECISION,
    "vibracion_rms_mm_s_media_1h" DOUBLE PRECISION,
    "vibracion_rms_mm_s_std_1h" DOUBLE PRECISION,
    "vibracion_rms_mm_s_media_4h" DOUBLE PRECISION,
    "temperatura_rodamiento_c_media_1h" DOUBLE PRECISION,
    "temperatura_rodamiento_c_std_1h" DOUBLE PRECISION,
    "temperatura_rodamiento_c_media_4h" DOUBLE PRECISION,
    "temperatura_motor_c_media_1h" DOUBLE PRECISION,
    "temperatura_motor_c_std_1h" DOUBLE PRECISION,
    "temperatura_motor_c_media_4h" DOUBLE PRECISION,
    "temperatura_aceite_c_media_1h" DOUBLE PRECISION,
    "temperatura_aceite_c_std_1h" DOUBLE PRECISION,
    "temperatura_aceite_c_media_4h" DOUBLE PRECISION,
    "presion_aceite_bar_media_1h" DOUBLE PRECISION,
    "presion_aceite_bar_std_1h" DOUBLE PRECISION,
    "presion_aceite_bar_media_4h" DOUBLE PRECISION,
    "presion_hidraulica_bar_media_1h" DOUBLE PRECISION,
    "presion_hidraulica_bar_std_1h" DOUBLE PRECISION,
    "presion_hidraulica_bar_media_4h" DOUBLE PRECISION,
    "caudal_refrigeracion_l_min_media_1h" DOUBLE PRECISION,
    "caudal_refrigeracion_l_min_std_1h" DOUBLE PRECISION,
    "caudal_refrigeracion_l_min_media_4h" DOUBLE PRECISION,
    "corriente_motor_pct_nominal_media_1h" DOUBLE PRECISION,
    "corriente_motor_pct_nominal_std_1h" DOUBLE PRECISION,
    "corriente_motor_pct_nominal_media_4h" DOUBLE PRECISION,
    "velocidad_motor_rpm_media_1h" DOUBLE PRECISION,
    "velocidad_motor_rpm_std_1h" DOUBLE PRECISION,
    "velocidad_motor_rpm_media_4h" DOUBLE PRECISION,
    "fraccion_marcha_4h" DOUBLE PRECISION,
    "fraccion_ausentes_1h" DOUBLE PRECISION,
    PRIMARY KEY ("equipo_id", "timestamp")
);

CREATE TABLE IF NOT EXISTS acb_demo.targets (
    "equipo_id" TEXT,
    "timestamp" TIMESTAMPTZ,
    "proximo_fallo_id" TEXT,
    "horas_hasta_proximo_fallo_observado" DOUBLE PRECISION,
    "fallo_4h" BIGINT,
    "censura_4h" TEXT,
    "fallo_8h" BIGINT,
    "censura_8h" TEXT,
    "fallo_24h" BIGINT,
    "censura_24h" TEXT,
    "particion" TEXT,
    PRIMARY KEY ("equipo_id", "timestamp")
);

DO $$ BEGIN ALTER TABLE acb_demo.fallos ADD CONSTRAINT fk_fallos_equipo_id FOREIGN KEY (equipo_id) REFERENCES acb_demo.equipos (equipo_id); EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN ALTER TABLE acb_demo.mantenimiento ADD CONSTRAINT fk_mantenimiento_equipo_id FOREIGN KEY (equipo_id) REFERENCES acb_demo.equipos (equipo_id); EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN ALTER TABLE acb_demo.mantenimiento ADD CONSTRAINT fk_mantenimiento_evento_id FOREIGN KEY (evento_id) REFERENCES acb_demo.fallos (evento_id); EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN ALTER TABLE acb_demo.bobinas ADD CONSTRAINT fk_bobinas_grado_acero FOREIGN KEY (grado_acero) REFERENCES acb_demo.productos (grado_acero); EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN ALTER TABLE acb_demo.bobinas ADD CONSTRAINT fk_bobinas_bobinadora_id FOREIGN KEY (bobinadora_id) REFERENCES acb_demo.equipos (equipo_id); EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN ALTER TABLE acb_demo.paradas_linea ADD CONSTRAINT fk_paradas_linea_evento_id FOREIGN KEY (evento_id) REFERENCES acb_demo.fallos (evento_id); EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN ALTER TABLE acb_demo.paradas_linea ADD CONSTRAINT fk_paradas_linea_equipo_causa FOREIGN KEY (equipo_causa) REFERENCES acb_demo.equipos (equipo_id); EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN ALTER TABLE acb_demo.estado_linea ADD CONSTRAINT fk_estado_linea_bobina_id FOREIGN KEY (bobina_id) REFERENCES acb_demo.bobinas (bobina_id); EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN ALTER TABLE acb_demo.telemetria ADD CONSTRAINT fk_telemetria_equipo_id FOREIGN KEY (equipo_id) REFERENCES acb_demo.equipos (equipo_id); EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN ALTER TABLE acb_demo.telemetria ADD CONSTRAINT fk_telemetria_bobina_id FOREIGN KEY (bobina_id) REFERENCES acb_demo.bobinas (bobina_id); EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN ALTER TABLE acb_demo.features ADD CONSTRAINT fk_features_equipo_id FOREIGN KEY (equipo_id) REFERENCES acb_demo.equipos (equipo_id); EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN ALTER TABLE acb_demo.targets ADD CONSTRAINT fk_targets_equipo_id FOREIGN KEY (equipo_id) REFERENCES acb_demo.equipos (equipo_id); EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE INDEX IF NOT EXISTS idx_fallos_t ON acb_demo.fallos (equipo_id, inicio);

CREATE INDEX IF NOT EXISTS idx_features_t ON acb_demo.features (timestamp);

COMMIT;