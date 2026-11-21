-- Datos 100% sintéticos. Crear únicamente en una base de pruebas. No sobrescribe esquemas existentes.

-- Ejecutar todo dentro de una transacción; el cargador lo hace automáticamente.

CREATE SCHEMA acb_motor_v4_0;

CREATE SCHEMA acb_motor_v4_0_truth;

REVOKE ALL ON SCHEMA acb_motor_v4_0_truth FROM PUBLIC;

CREATE TABLE acb_motor_v4_0.activos (
    "asset_id" TEXT NOT NULL,
    "parent_asset_id" TEXT,
    "asset_type" TEXT,
    "description" TEXT,
    "is_synthetic" BOOLEAN,
    PRIMARY KEY ("asset_id"),
    CHECK (is_synthetic)
);

CREATE TABLE acb_motor_v4_0.catalogo_archivos (
    "relative_path" TEXT NOT NULL,
    "table_name" TEXT,
    "row_count" BIGINT,
    "sha256" TEXT,
    PRIMARY KEY ("relative_path"),
    CHECK (row_count >= 0)
);

CREATE TABLE acb_motor_v4_0.configuraciones (
    "configuration_id" TEXT NOT NULL,
    "stand_id" TEXT,
    "valid_from" TIMESTAMPTZ,
    "valid_to" TIMESTAMPTZ,
    "known_at" TIMESTAMPTZ,
    "drive_version" TEXT,
    "control_version" TEXT,
    "sensor_version" TEXT,
    "maintenance_policy_version" TEXT,
    "roll_radius_m" DOUBLE PRECISION,
    "gear_ratio" DOUBLE PRECISION,
    "transmission_efficiency" DOUBLE PRECISION,
    "motor_efficiency" DOUBLE PRECISION,
    "voltage_ll_v" DOUBLE PRECISION,
    "power_factor" DOUBLE PRECISION,
    "rated_mechanical_kw" DOUBLE PRECISION,
    "forward_slip" DOUBLE PRECISION,
    "sensor_gain" DOUBLE PRECISION,
    "evidence_status" TEXT,
    "is_synthetic" BOOLEAN,
    PRIMARY KEY ("configuration_id"),
    CHECK (valid_to > valid_from),
    CHECK (known_at <= valid_from),
    CHECK (gear_ratio > 0),
    CHECK (roll_radius_m > 0),
    CHECK (motor_efficiency BETWEEN 0 AND 1),
    CHECK (transmission_efficiency BETWEEN 0 AND 1),
    CHECK (power_factor > 0 AND power_factor <= 1),
    CHECK (voltage_ll_v > 0),
    CHECK (is_synthetic)
);

CREATE TABLE acb_motor_v4_0.ejecuciones (
    "run_id" TEXT NOT NULL,
    "assembly_id" TEXT,
    "seed" BIGINT,
    "subseed_index" BIGINT,
    "version" TEXT,
    "start" TIMESTAMPTZ,
    "end" TIMESTAMPTZ,
    "scenario" TEXT,
    "step_minutes" BIGINT,
    "decision_minutes" BIGINT,
    "config_sha256" TEXT,
    PRIMARY KEY ("run_id"),
    CHECK ("end" > "start"),
    CHECK (step_minutes = 5),
    CHECK (decision_minutes = 15)
);

CREATE TABLE acb_motor_v4_0.fallos (
    "run_id" TEXT NOT NULL,
    "event_id" TEXT NOT NULL,
    "assembly_id" TEXT,
    "asset_id" TEXT,
    "start" TIMESTAMPTZ,
    "end" TIMESTAMPTZ,
    "mode" TEXT,
    "onset" TEXT,
    "detected_at" TIMESTAMPTZ,
    "diagnosis_available_at" TIMESTAMPTZ,
    PRIMARY KEY ("run_id", "event_id"),
    CHECK ("end" > "start"),
    CHECK (diagnosis_available_at >= "start")
);

CREATE TABLE acb_motor_v4_0.mantenimiento (
    "run_id" TEXT NOT NULL,
    "maintenance_id" TEXT NOT NULL,
    "assembly_id" TEXT,
    "asset_id" TEXT,
    "start" TIMESTAMPTZ,
    "end" TIMESTAMPTZ,
    "kind" TEXT,
    "event_id" TEXT,
    "known_at" TIMESTAMPTZ,
    "result_available_at" TIMESTAMPTZ,
    "action" TEXT,
    "completed_operating_hours" DOUBLE PRECISION,
    PRIMARY KEY ("run_id", "maintenance_id"),
    CHECK ("end" > "start"),
    CHECK (result_available_at >= "end")
);

CREATE TABLE acb_motor_v4_0.plan_mantenimiento (
    "run_id" TEXT NOT NULL,
    "plan_id" TEXT NOT NULL,
    "revision" BIGINT NOT NULL,
    "known_at" TIMESTAMPTZ,
    "scheduled_start" TIMESTAMPTZ,
    "status" TEXT,
    "planned_duration_hours" BIGINT,
    PRIMARY KEY ("run_id", "plan_id", "revision"),
    CHECK (revision >= 1),
    CHECK (status IN ('previsto','aplazado_correctivo','iniciado')),
    CHECK ((status = 'aplazado_correctivo') = (scheduled_start IS NULL)),
    CHECK (planned_duration_hours > 0)
);

CREATE TABLE acb_motor_v4_0.productos (
    "grado_acero" TEXT NOT NULL,
    "espesor_min_demo_mm" DOUBLE PRECISION,
    "factor_carga_demo" DOUBLE PRECISION,
    PRIMARY KEY ("grado_acero")
);

CREATE TABLE acb_motor_v4_0.segmentos_produccion (
    "run_id" TEXT NOT NULL,
    "assembly_id" TEXT,
    "stand_id" TEXT,
    "configuration_id" TEXT,
    "rolling_state" TEXT,
    "production_segment_id" TEXT,
    "steel_family" TEXT,
    "target_thickness_mm" DOUBLE PRECISION,
    "width_mm" DOUBLE PRECISION,
    "segment_id" TEXT NOT NULL,
    "start" TIMESTAMPTZ,
    "end" TIMESTAMPTZ,
    "known_at" TIMESTAMPTZ,
    PRIMARY KEY ("run_id", "segment_id"),
    CHECK ("end" > "start"),
    CHECK (known_at <= "start")
);

CREATE TABLE acb_motor_v4_0.sensores (
    "sensor_id" TEXT NOT NULL,
    "asset_id" TEXT,
    "variable" TEXT,
    "unit" TEXT,
    "min_demo" BIGINT,
    "max_demo" BIGINT,
    "method" TEXT,
    "is_synthetic" BOOLEAN,
    "descriptor_type" TEXT,
    "axis" TEXT,
    "mounting" TEXT,
    "sampling_frequency_hz" DOUBLE PRECISION,
    "bandwidth_low_hz" DOUBLE PRECISION,
    "bandwidth_high_hz" DOUBLE PRECISION,
    "aggregation_window_seconds" DOUBLE PRECISION,
    "output_interval_seconds" BIGINT,
    "contract_status" TEXT,
    PRIMARY KEY ("sensor_id"),
    CHECK (is_synthetic),
    CHECK (max_demo > min_demo)
);

CREATE TABLE acb_motor_v4_0.telemetria (
    "run_id" TEXT NOT NULL,
    "assembly_id" TEXT NOT NULL,
    "timestamp" TIMESTAMPTZ NOT NULL,
    "bearing_temperature_de_c" DOUBLE PRECISION,
    "bearing_temperature_nde_c" DOUBLE PRECISION,
    "winding_temperature_c" DOUBLE PRECISION,
    "vibration_de_mm_s" DOUBLE PRECISION,
    "vibration_nde_mm_s" DOUBLE PRECISION,
    "acceleration_de_m_s2" DOUBLE PRECISION,
    "acceleration_nde_m_s2" DOUBLE PRECISION,
    "kurtosis_de" DOUBLE PRECISION,
    "kurtosis_nde" DOUBLE PRECISION,
    "current_a" DOUBLE PRECISION,
    "load_ratio" DOUBLE PRECISION,
    "motor_speed_rpm" DOUBLE PRECISION,
    "ambient_temperature_c" DOUBLE PRECISION,
    "cooling_flow_l_min" DOUBLE PRECISION,
    "lubrication_pressure_bar" DOUBLE PRECISION,
    "roll_speed_rpm" DOUBLE PRECISION,
    "strip_speed_m_s" DOUBLE PRECISION,
    "strip_entry_speed_m_s" DOUBLE PRECISION,
    "entry_thickness_mm" DOUBLE PRECISION,
    "exit_thickness_mm" DOUBLE PRECISION,
    "strip_temperature_c" DOUBLE PRECISION,
    "rolling_force_kn" DOUBLE PRECISION,
    "roll_torque_knm" DOUBLE PRECISION,
    "motor_torque_knm" DOUBLE PRECISION,
    "mechanical_power_kw" DOUBLE PRECISION,
    "electrical_power_kw" DOUBLE PRECISION,
    "available_at" TIMESTAMPTZ,
    "stand_id" TEXT,
    "configuration_id" TEXT,
    "rolling_state" TEXT,
    "production_segment_id" TEXT,
    "steel_family" TEXT,
    "target_thickness_mm" DOUBLE PRECISION,
    "width_mm" DOUBLE PRECISION,
    "run_hours_since_service" DOUBLE PRECISION,
    "known_service_type" TEXT,
    "starts_last_24h" BIGINT,
    PRIMARY KEY ("run_id", "assembly_id", "timestamp"),
    CHECK (available_at >= "timestamp")
);

CREATE TABLE acb_motor_v4_0.features (
    "run_id" TEXT NOT NULL,
    "assembly_id" TEXT NOT NULL,
    "timestamp" TIMESTAMPTZ NOT NULL,
    "stand_id" TEXT,
    "configuration_id" TEXT,
    "production_segment_id" TEXT,
    "rolling_state" TEXT,
    "steel_family" TEXT,
    "target_thickness_mm" DOUBLE PRECISION,
    "width_mm" DOUBLE PRECISION,
    "run_hours_since_service" DOUBLE PRECISION,
    "known_service_type" TEXT,
    "starts_last_24h" BIGINT,
    "coverage_min_30m" DOUBLE PRECISION,
    "missing_fraction_30m" DOUBLE PRECISION,
    "out_of_range_fraction_30m" DOUBLE PRECISION,
    "sensor_stale" BOOLEAN,
    "max_data_age_minutes" DOUBLE PRECISION,
    "source_available_at_max" TIMESTAMPTZ,
    "eligible_operation" BOOLEAN,
    "evaluation_status" TEXT,
    "quality_code" TEXT,
    "bearing_temperature_de_c" DOUBLE PRECISION,
    "bearing_temperature_nde_c" DOUBLE PRECISION,
    "winding_temperature_c" DOUBLE PRECISION,
    "vibration_de_mm_s" DOUBLE PRECISION,
    "vibration_nde_mm_s" DOUBLE PRECISION,
    "acceleration_de_m_s2" DOUBLE PRECISION,
    "acceleration_nde_m_s2" DOUBLE PRECISION,
    "kurtosis_de" DOUBLE PRECISION,
    "kurtosis_nde" DOUBLE PRECISION,
    "current_a" DOUBLE PRECISION,
    "load_ratio" DOUBLE PRECISION,
    "motor_speed_rpm" DOUBLE PRECISION,
    "ambient_temperature_c" DOUBLE PRECISION,
    "cooling_flow_l_min" DOUBLE PRECISION,
    "lubrication_pressure_bar" DOUBLE PRECISION,
    "roll_speed_rpm" DOUBLE PRECISION,
    "strip_speed_m_s" DOUBLE PRECISION,
    "strip_entry_speed_m_s" DOUBLE PRECISION,
    "entry_thickness_mm" DOUBLE PRECISION,
    "exit_thickness_mm" DOUBLE PRECISION,
    "strip_temperature_c" DOUBLE PRECISION,
    "rolling_force_kn" DOUBLE PRECISION,
    "roll_torque_knm" DOUBLE PRECISION,
    "motor_torque_knm" DOUBLE PRECISION,
    "mechanical_power_kw" DOUBLE PRECISION,
    "electrical_power_kw" DOUBLE PRECISION,
    "bearing_temperature_de_c_mean_30m" DOUBLE PRECISION,
    "bearing_temperature_de_c_std_30m" DOUBLE PRECISION,
    "bearing_temperature_de_c_slope_per_h_30m" DOUBLE PRECISION,
    "bearing_temperature_nde_c_mean_30m" DOUBLE PRECISION,
    "bearing_temperature_nde_c_std_30m" DOUBLE PRECISION,
    "bearing_temperature_nde_c_slope_per_h_30m" DOUBLE PRECISION,
    "winding_temperature_c_mean_30m" DOUBLE PRECISION,
    "winding_temperature_c_std_30m" DOUBLE PRECISION,
    "winding_temperature_c_slope_per_h_30m" DOUBLE PRECISION,
    "vibration_de_mm_s_mean_30m" DOUBLE PRECISION,
    "vibration_de_mm_s_std_30m" DOUBLE PRECISION,
    "vibration_de_mm_s_slope_per_h_30m" DOUBLE PRECISION,
    "vibration_nde_mm_s_mean_30m" DOUBLE PRECISION,
    "vibration_nde_mm_s_std_30m" DOUBLE PRECISION,
    "vibration_nde_mm_s_slope_per_h_30m" DOUBLE PRECISION,
    "acceleration_de_m_s2_mean_30m" DOUBLE PRECISION,
    "acceleration_de_m_s2_std_30m" DOUBLE PRECISION,
    "acceleration_de_m_s2_slope_per_h_30m" DOUBLE PRECISION,
    "acceleration_nde_m_s2_mean_30m" DOUBLE PRECISION,
    "acceleration_nde_m_s2_std_30m" DOUBLE PRECISION,
    "acceleration_nde_m_s2_slope_per_h_30m" DOUBLE PRECISION,
    "kurtosis_de_mean_30m" DOUBLE PRECISION,
    "kurtosis_de_std_30m" DOUBLE PRECISION,
    "kurtosis_de_slope_per_h_30m" DOUBLE PRECISION,
    "kurtosis_nde_mean_30m" DOUBLE PRECISION,
    "kurtosis_nde_std_30m" DOUBLE PRECISION,
    "kurtosis_nde_slope_per_h_30m" DOUBLE PRECISION,
    "current_a_mean_30m" DOUBLE PRECISION,
    "current_a_std_30m" DOUBLE PRECISION,
    "current_a_slope_per_h_30m" DOUBLE PRECISION,
    "load_ratio_mean_30m" DOUBLE PRECISION,
    "load_ratio_std_30m" DOUBLE PRECISION,
    "load_ratio_slope_per_h_30m" DOUBLE PRECISION,
    "motor_speed_rpm_mean_30m" DOUBLE PRECISION,
    "motor_speed_rpm_std_30m" DOUBLE PRECISION,
    "motor_speed_rpm_slope_per_h_30m" DOUBLE PRECISION,
    "ambient_temperature_c_mean_30m" DOUBLE PRECISION,
    "ambient_temperature_c_std_30m" DOUBLE PRECISION,
    "ambient_temperature_c_slope_per_h_30m" DOUBLE PRECISION,
    "cooling_flow_l_min_mean_30m" DOUBLE PRECISION,
    "cooling_flow_l_min_std_30m" DOUBLE PRECISION,
    "cooling_flow_l_min_slope_per_h_30m" DOUBLE PRECISION,
    "lubrication_pressure_bar_mean_30m" DOUBLE PRECISION,
    "lubrication_pressure_bar_std_30m" DOUBLE PRECISION,
    "lubrication_pressure_bar_slope_per_h_30m" DOUBLE PRECISION,
    "roll_speed_rpm_mean_30m" DOUBLE PRECISION,
    "roll_speed_rpm_std_30m" DOUBLE PRECISION,
    "roll_speed_rpm_slope_per_h_30m" DOUBLE PRECISION,
    "strip_speed_m_s_mean_30m" DOUBLE PRECISION,
    "strip_speed_m_s_std_30m" DOUBLE PRECISION,
    "strip_speed_m_s_slope_per_h_30m" DOUBLE PRECISION,
    "strip_entry_speed_m_s_mean_30m" DOUBLE PRECISION,
    "strip_entry_speed_m_s_std_30m" DOUBLE PRECISION,
    "strip_entry_speed_m_s_slope_per_h_30m" DOUBLE PRECISION,
    "entry_thickness_mm_mean_30m" DOUBLE PRECISION,
    "entry_thickness_mm_std_30m" DOUBLE PRECISION,
    "entry_thickness_mm_slope_per_h_30m" DOUBLE PRECISION,
    "exit_thickness_mm_mean_30m" DOUBLE PRECISION,
    "exit_thickness_mm_std_30m" DOUBLE PRECISION,
    "exit_thickness_mm_slope_per_h_30m" DOUBLE PRECISION,
    "strip_temperature_c_mean_30m" DOUBLE PRECISION,
    "strip_temperature_c_std_30m" DOUBLE PRECISION,
    "strip_temperature_c_slope_per_h_30m" DOUBLE PRECISION,
    "rolling_force_kn_mean_30m" DOUBLE PRECISION,
    "rolling_force_kn_std_30m" DOUBLE PRECISION,
    "rolling_force_kn_slope_per_h_30m" DOUBLE PRECISION,
    "roll_torque_knm_mean_30m" DOUBLE PRECISION,
    "roll_torque_knm_std_30m" DOUBLE PRECISION,
    "roll_torque_knm_slope_per_h_30m" DOUBLE PRECISION,
    "motor_torque_knm_mean_30m" DOUBLE PRECISION,
    "motor_torque_knm_std_30m" DOUBLE PRECISION,
    "motor_torque_knm_slope_per_h_30m" DOUBLE PRECISION,
    "mechanical_power_kw_mean_30m" DOUBLE PRECISION,
    "mechanical_power_kw_std_30m" DOUBLE PRECISION,
    "mechanical_power_kw_slope_per_h_30m" DOUBLE PRECISION,
    "electrical_power_kw_mean_30m" DOUBLE PRECISION,
    "electrical_power_kw_std_30m" DOUBLE PRECISION,
    "electrical_power_kw_slope_per_h_30m" DOUBLE PRECISION,
    "bearing_temperature_de_c_mean_240m" DOUBLE PRECISION,
    "bearing_temperature_de_c_std_240m" DOUBLE PRECISION,
    "bearing_temperature_de_c_slope_per_h_240m" DOUBLE PRECISION,
    "bearing_temperature_nde_c_mean_240m" DOUBLE PRECISION,
    "bearing_temperature_nde_c_std_240m" DOUBLE PRECISION,
    "bearing_temperature_nde_c_slope_per_h_240m" DOUBLE PRECISION,
    "winding_temperature_c_mean_240m" DOUBLE PRECISION,
    "winding_temperature_c_std_240m" DOUBLE PRECISION,
    "winding_temperature_c_slope_per_h_240m" DOUBLE PRECISION,
    "vibration_de_mm_s_mean_240m" DOUBLE PRECISION,
    "vibration_de_mm_s_std_240m" DOUBLE PRECISION,
    "vibration_de_mm_s_slope_per_h_240m" DOUBLE PRECISION,
    "vibration_nde_mm_s_mean_240m" DOUBLE PRECISION,
    "vibration_nde_mm_s_std_240m" DOUBLE PRECISION,
    "vibration_nde_mm_s_slope_per_h_240m" DOUBLE PRECISION,
    "acceleration_de_m_s2_mean_240m" DOUBLE PRECISION,
    "acceleration_de_m_s2_std_240m" DOUBLE PRECISION,
    "acceleration_de_m_s2_slope_per_h_240m" DOUBLE PRECISION,
    "acceleration_nde_m_s2_mean_240m" DOUBLE PRECISION,
    "acceleration_nde_m_s2_std_240m" DOUBLE PRECISION,
    "acceleration_nde_m_s2_slope_per_h_240m" DOUBLE PRECISION,
    "kurtosis_de_mean_240m" DOUBLE PRECISION,
    "kurtosis_de_std_240m" DOUBLE PRECISION,
    "kurtosis_de_slope_per_h_240m" DOUBLE PRECISION,
    "kurtosis_nde_mean_240m" DOUBLE PRECISION,
    "kurtosis_nde_std_240m" DOUBLE PRECISION,
    "kurtosis_nde_slope_per_h_240m" DOUBLE PRECISION,
    "current_a_mean_240m" DOUBLE PRECISION,
    "current_a_std_240m" DOUBLE PRECISION,
    "current_a_slope_per_h_240m" DOUBLE PRECISION,
    "load_ratio_mean_240m" DOUBLE PRECISION,
    "load_ratio_std_240m" DOUBLE PRECISION,
    "load_ratio_slope_per_h_240m" DOUBLE PRECISION,
    "motor_speed_rpm_mean_240m" DOUBLE PRECISION,
    "motor_speed_rpm_std_240m" DOUBLE PRECISION,
    "motor_speed_rpm_slope_per_h_240m" DOUBLE PRECISION,
    "ambient_temperature_c_mean_240m" DOUBLE PRECISION,
    "ambient_temperature_c_std_240m" DOUBLE PRECISION,
    "ambient_temperature_c_slope_per_h_240m" DOUBLE PRECISION,
    "cooling_flow_l_min_mean_240m" DOUBLE PRECISION,
    "cooling_flow_l_min_std_240m" DOUBLE PRECISION,
    "cooling_flow_l_min_slope_per_h_240m" DOUBLE PRECISION,
    "lubrication_pressure_bar_mean_240m" DOUBLE PRECISION,
    "lubrication_pressure_bar_std_240m" DOUBLE PRECISION,
    "lubrication_pressure_bar_slope_per_h_240m" DOUBLE PRECISION,
    "roll_speed_rpm_mean_240m" DOUBLE PRECISION,
    "roll_speed_rpm_std_240m" DOUBLE PRECISION,
    "roll_speed_rpm_slope_per_h_240m" DOUBLE PRECISION,
    "strip_speed_m_s_mean_240m" DOUBLE PRECISION,
    "strip_speed_m_s_std_240m" DOUBLE PRECISION,
    "strip_speed_m_s_slope_per_h_240m" DOUBLE PRECISION,
    "strip_entry_speed_m_s_mean_240m" DOUBLE PRECISION,
    "strip_entry_speed_m_s_std_240m" DOUBLE PRECISION,
    "strip_entry_speed_m_s_slope_per_h_240m" DOUBLE PRECISION,
    "entry_thickness_mm_mean_240m" DOUBLE PRECISION,
    "entry_thickness_mm_std_240m" DOUBLE PRECISION,
    "entry_thickness_mm_slope_per_h_240m" DOUBLE PRECISION,
    "exit_thickness_mm_mean_240m" DOUBLE PRECISION,
    "exit_thickness_mm_std_240m" DOUBLE PRECISION,
    "exit_thickness_mm_slope_per_h_240m" DOUBLE PRECISION,
    "strip_temperature_c_mean_240m" DOUBLE PRECISION,
    "strip_temperature_c_std_240m" DOUBLE PRECISION,
    "strip_temperature_c_slope_per_h_240m" DOUBLE PRECISION,
    "rolling_force_kn_mean_240m" DOUBLE PRECISION,
    "rolling_force_kn_std_240m" DOUBLE PRECISION,
    "rolling_force_kn_slope_per_h_240m" DOUBLE PRECISION,
    "roll_torque_knm_mean_240m" DOUBLE PRECISION,
    "roll_torque_knm_std_240m" DOUBLE PRECISION,
    "roll_torque_knm_slope_per_h_240m" DOUBLE PRECISION,
    "motor_torque_knm_mean_240m" DOUBLE PRECISION,
    "motor_torque_knm_std_240m" DOUBLE PRECISION,
    "motor_torque_knm_slope_per_h_240m" DOUBLE PRECISION,
    "mechanical_power_kw_mean_240m" DOUBLE PRECISION,
    "mechanical_power_kw_std_240m" DOUBLE PRECISION,
    "mechanical_power_kw_slope_per_h_240m" DOUBLE PRECISION,
    "electrical_power_kw_mean_240m" DOUBLE PRECISION,
    "electrical_power_kw_std_240m" DOUBLE PRECISION,
    "electrical_power_kw_slope_per_h_240m" DOUBLE PRECISION,
    PRIMARY KEY ("run_id", "assembly_id", "timestamp"),
    CHECK (coverage_min_30m BETWEEN 0 AND 1),
    CHECK (missing_fraction_30m BETWEEN 0 AND 1),
    CHECK (source_available_at_max <= "timestamp")
);

CREATE TABLE acb_motor_v4_0_truth.episodios (
    "run_id" TEXT NOT NULL,
    "episode_id" TEXT NOT NULL,
    "asset_id" TEXT,
    "start" TIMESTAMPTZ,
    "end" TIMESTAMPTZ,
    PRIMARY KEY ("run_id", "episode_id"),
    CHECK ("end" > "start")
);

CREATE TABLE acb_motor_v4_0_truth.incidencias_sensores (
    "run_id" TEXT NOT NULL,
    "incident_id" TEXT NOT NULL,
    "sensor_id" TEXT,
    "start" TIMESTAMPTZ,
    "end" TIMESTAMPTZ,
    "kind" TEXT,
    PRIMARY KEY ("run_id", "incident_id"),
    CHECK ("end" > "start")
);

CREATE TABLE acb_motor_v4_0_truth.reparaciones (
    "run_id" TEXT NOT NULL,
    "maintenance_id" TEXT NOT NULL,
    "asset_id" TEXT NOT NULL,
    "damage_before" DOUBLE PRECISION,
    "damage_after" DOUBLE PRECISION,
    "action" TEXT,
    PRIMARY KEY ("run_id", "maintenance_id", "asset_id"),
    CHECK (damage_after <= damage_before)
);

CREATE TABLE acb_motor_v4_0_truth.fisica (
    "roll_speed_rpm" DOUBLE PRECISION,
    "strip_speed_m_s" DOUBLE PRECISION,
    "strip_entry_speed_m_s" DOUBLE PRECISION,
    "entry_thickness_mm" DOUBLE PRECISION,
    "exit_thickness_mm" DOUBLE PRECISION,
    "strip_temperature_c" DOUBLE PRECISION,
    "rolling_force_kn" DOUBLE PRECISION,
    "roll_torque_knm" DOUBLE PRECISION,
    "motor_torque_knm" DOUBLE PRECISION,
    "mechanical_power_kw" DOUBLE PRECISION,
    "electrical_power_kw" DOUBLE PRECISION,
    "run_id" TEXT NOT NULL,
    "assembly_id" TEXT NOT NULL,
    "timestamp" TIMESTAMPTZ NOT NULL,
    "motor_speed_rpm" DOUBLE PRECISION,
    "current_a" DOUBLE PRECISION,
    "load_ratio" DOUBLE PRECISION,
    "motor_efficiency_effective" DOUBLE PRECISION,
    "width_mm" DOUBLE PRECISION,
    PRIMARY KEY ("run_id", "assembly_id", "timestamp")
);

CREATE TABLE acb_motor_v4_0_truth.estado_latente (
    "run_id" TEXT NOT NULL,
    "assembly_id" TEXT NOT NULL,
    "timestamp" TIMESTAMPTZ NOT NULL,
    "damage_de" DOUBLE PRECISION,
    "damage_nde" DOUBLE PRECISION,
    "damage_motor" DOUBLE PRECISION,
    "health_state" TEXT,
    PRIMARY KEY ("run_id", "assembly_id", "timestamp")
);

CREATE TABLE acb_motor_v4_0_truth.targets (
    "run_id" TEXT NOT NULL,
    "assembly_id" TEXT NOT NULL,
    "timestamp" TIMESTAMPTZ NOT NULL,
    "y24" BIGINT,
    "censor_reason" TEXT,
    "event_id" TEXT,
    "partition" TEXT,
    "exclusion_reason" TEXT,
    "healthy_reference_if" BOOLEAN,
    "if_reference_observable" BOOLEAN,
    PRIMARY KEY ("run_id", "assembly_id", "timestamp"),
    CHECK (y24 IN (0,1)),
    CHECK (partition IN ('train','validation','test','stress','excluida')),
    CHECK ((y24 IS NULL) = (censor_reason <> 'ninguna'))
);

ALTER TABLE acb_motor_v4_0.configuraciones ADD FOREIGN KEY ("stand_id") REFERENCES acb_motor_v4_0.activos ("asset_id");

ALTER TABLE acb_motor_v4_0.telemetria ADD FOREIGN KEY ("configuration_id") REFERENCES acb_motor_v4_0.configuraciones ("configuration_id");

ALTER TABLE acb_motor_v4_0.telemetria ADD FOREIGN KEY ("stand_id") REFERENCES acb_motor_v4_0.activos ("asset_id");

ALTER TABLE acb_motor_v4_0.features ADD FOREIGN KEY ("configuration_id") REFERENCES acb_motor_v4_0.configuraciones ("configuration_id");

ALTER TABLE acb_motor_v4_0.features ADD FOREIGN KEY ("stand_id") REFERENCES acb_motor_v4_0.activos ("asset_id");

ALTER TABLE acb_motor_v4_0.segmentos_produccion ADD FOREIGN KEY ("configuration_id") REFERENCES acb_motor_v4_0.configuraciones ("configuration_id");

ALTER TABLE acb_motor_v4_0.segmentos_produccion ADD FOREIGN KEY ("stand_id") REFERENCES acb_motor_v4_0.activos ("asset_id");

ALTER TABLE acb_motor_v4_0.telemetria ADD FOREIGN KEY ("run_id", "production_segment_id") REFERENCES acb_motor_v4_0.segmentos_produccion ("run_id", "segment_id");

ALTER TABLE acb_motor_v4_0_truth.fisica ADD FOREIGN KEY ("run_id", "assembly_id", "timestamp") REFERENCES acb_motor_v4_0.telemetria ("run_id", "assembly_id", "timestamp");

ALTER TABLE acb_motor_v4_0.activos ADD FOREIGN KEY ("parent_asset_id") REFERENCES acb_motor_v4_0.activos ("asset_id");

ALTER TABLE acb_motor_v4_0.sensores ADD FOREIGN KEY ("asset_id") REFERENCES acb_motor_v4_0.activos ("asset_id");

ALTER TABLE acb_motor_v4_0.ejecuciones ADD FOREIGN KEY ("assembly_id") REFERENCES acb_motor_v4_0.activos ("asset_id");

ALTER TABLE acb_motor_v4_0.fallos ADD FOREIGN KEY ("run_id") REFERENCES acb_motor_v4_0.ejecuciones ("run_id");

ALTER TABLE acb_motor_v4_0.fallos ADD FOREIGN KEY ("assembly_id") REFERENCES acb_motor_v4_0.activos ("asset_id");

ALTER TABLE acb_motor_v4_0.fallos ADD FOREIGN KEY ("asset_id") REFERENCES acb_motor_v4_0.activos ("asset_id");

ALTER TABLE acb_motor_v4_0.mantenimiento ADD FOREIGN KEY ("run_id") REFERENCES acb_motor_v4_0.ejecuciones ("run_id");

ALTER TABLE acb_motor_v4_0.mantenimiento ADD FOREIGN KEY ("assembly_id") REFERENCES acb_motor_v4_0.activos ("asset_id");

ALTER TABLE acb_motor_v4_0.mantenimiento ADD FOREIGN KEY ("asset_id") REFERENCES acb_motor_v4_0.activos ("asset_id");

ALTER TABLE acb_motor_v4_0.plan_mantenimiento ADD FOREIGN KEY ("run_id") REFERENCES acb_motor_v4_0.ejecuciones ("run_id");

ALTER TABLE acb_motor_v4_0.segmentos_produccion ADD FOREIGN KEY ("run_id") REFERENCES acb_motor_v4_0.ejecuciones ("run_id");

ALTER TABLE acb_motor_v4_0.segmentos_produccion ADD FOREIGN KEY ("assembly_id") REFERENCES acb_motor_v4_0.activos ("asset_id");

ALTER TABLE acb_motor_v4_0.telemetria ADD FOREIGN KEY ("run_id") REFERENCES acb_motor_v4_0.ejecuciones ("run_id");

ALTER TABLE acb_motor_v4_0.telemetria ADD FOREIGN KEY ("assembly_id") REFERENCES acb_motor_v4_0.activos ("asset_id");

ALTER TABLE acb_motor_v4_0.features ADD FOREIGN KEY ("run_id") REFERENCES acb_motor_v4_0.ejecuciones ("run_id");

ALTER TABLE acb_motor_v4_0.features ADD FOREIGN KEY ("assembly_id") REFERENCES acb_motor_v4_0.activos ("asset_id");

ALTER TABLE acb_motor_v4_0_truth.episodios ADD FOREIGN KEY ("run_id") REFERENCES acb_motor_v4_0.ejecuciones ("run_id");

ALTER TABLE acb_motor_v4_0_truth.episodios ADD FOREIGN KEY ("asset_id") REFERENCES acb_motor_v4_0.activos ("asset_id");

ALTER TABLE acb_motor_v4_0_truth.incidencias_sensores ADD FOREIGN KEY ("run_id") REFERENCES acb_motor_v4_0.ejecuciones ("run_id");

ALTER TABLE acb_motor_v4_0_truth.reparaciones ADD FOREIGN KEY ("run_id") REFERENCES acb_motor_v4_0.ejecuciones ("run_id");

ALTER TABLE acb_motor_v4_0_truth.reparaciones ADD FOREIGN KEY ("asset_id") REFERENCES acb_motor_v4_0.activos ("asset_id");

ALTER TABLE acb_motor_v4_0_truth.fisica ADD FOREIGN KEY ("run_id") REFERENCES acb_motor_v4_0.ejecuciones ("run_id");

ALTER TABLE acb_motor_v4_0_truth.fisica ADD FOREIGN KEY ("assembly_id") REFERENCES acb_motor_v4_0.activos ("asset_id");

ALTER TABLE acb_motor_v4_0_truth.estado_latente ADD FOREIGN KEY ("run_id") REFERENCES acb_motor_v4_0.ejecuciones ("run_id");

ALTER TABLE acb_motor_v4_0_truth.estado_latente ADD FOREIGN KEY ("assembly_id") REFERENCES acb_motor_v4_0.activos ("asset_id");

ALTER TABLE acb_motor_v4_0_truth.targets ADD FOREIGN KEY ("run_id") REFERENCES acb_motor_v4_0.ejecuciones ("run_id");

ALTER TABLE acb_motor_v4_0_truth.targets ADD FOREIGN KEY ("assembly_id") REFERENCES acb_motor_v4_0.activos ("asset_id");

ALTER TABLE acb_motor_v4_0.mantenimiento ADD FOREIGN KEY ("run_id", "event_id") REFERENCES acb_motor_v4_0.fallos ("run_id", "event_id");

ALTER TABLE acb_motor_v4_0.features ADD FOREIGN KEY ("run_id", "assembly_id", "timestamp") REFERENCES acb_motor_v4_0.telemetria ("run_id", "assembly_id", "timestamp");

ALTER TABLE acb_motor_v4_0_truth.targets ADD FOREIGN KEY ("run_id", "assembly_id", "timestamp") REFERENCES acb_motor_v4_0.features ("run_id", "assembly_id", "timestamp");

ALTER TABLE acb_motor_v4_0_truth.targets ADD FOREIGN KEY ("run_id", "event_id") REFERENCES acb_motor_v4_0.fallos ("run_id", "event_id");

ALTER TABLE acb_motor_v4_0_truth.estado_latente ADD FOREIGN KEY ("run_id", "assembly_id", "timestamp") REFERENCES acb_motor_v4_0.telemetria ("run_id", "assembly_id", "timestamp");

ALTER TABLE acb_motor_v4_0_truth.incidencias_sensores ADD FOREIGN KEY ("sensor_id") REFERENCES acb_motor_v4_0.sensores ("sensor_id");

ALTER TABLE acb_motor_v4_0_truth.reparaciones ADD FOREIGN KEY ("run_id", "maintenance_id") REFERENCES acb_motor_v4_0.mantenimiento ("run_id", "maintenance_id");

ALTER TABLE acb_motor_v4_0.telemetria ADD FOREIGN KEY ("steel_family") REFERENCES acb_motor_v4_0.productos ("grado_acero");

ALTER TABLE acb_motor_v4_0.features ADD FOREIGN KEY ("steel_family") REFERENCES acb_motor_v4_0.productos ("grado_acero");

ALTER TABLE acb_motor_v4_0.segmentos_produccion ADD FOREIGN KEY ("steel_family") REFERENCES acb_motor_v4_0.productos ("grado_acero");

CREATE INDEX ON acb_motor_v4_0.fallos (assembly_id, "start");

CREATE INDEX ON acb_motor_v4_0.features ("timestamp");

CREATE INDEX ON acb_motor_v4_0_truth.targets (partition);

REVOKE ALL ON ALL TABLES IN SCHEMA acb_motor_v4_0_truth FROM PUBLIC;

ALTER DEFAULT PRIVILEGES IN SCHEMA acb_motor_v4_0_truth REVOKE ALL ON TABLES FROM PUBLIC;
