-- Reproducir conocimiento en un instante. No concede acceso a tablas completas.
CREATE SCHEMA acb_motor_v4_0_api;
CREATE FUNCTION acb_motor_v4_0_api.features_asof(cutoff timestamptz)
RETURNS SETOF acb_motor_v4_0.features LANGUAGE sql STABLE SECURITY DEFINER
SET search_path=pg_catalog AS $$
 SELECT f.* FROM acb_motor_v4_0.features f WHERE f.timestamp<=cutoff;
$$;
CREATE FUNCTION acb_motor_v4_0_api.planes_asof(cutoff timestamptz)
RETURNS SETOF acb_motor_v4_0.plan_mantenimiento LANGUAGE sql STABLE SECURITY DEFINER
SET search_path=pg_catalog AS $$
 SELECT DISTINCT ON (run_id,plan_id) p.* FROM acb_motor_v4_0.plan_mantenimiento p
 WHERE known_at<=cutoff ORDER BY run_id,plan_id,known_at DESC,revision DESC;
$$;
CREATE FUNCTION acb_motor_v4_0_api.servicios_asof(cutoff timestamptz)
RETURNS TABLE(run_id text,maintenance_id text,asset_id text,start timestamptz,kind text,
 completed_end timestamptz,action text,completed_operating_hours double precision)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog AS $$
 SELECT run_id,maintenance_id,asset_id,start,kind,
 CASE WHEN result_available_at<=cutoff THEN "end" END,
 CASE WHEN result_available_at<=cutoff THEN action END,
 CASE WHEN result_available_at<=cutoff THEN completed_operating_hours END
 FROM acb_motor_v4_0.mantenimiento WHERE known_at<=cutoff;
$$;
-- Exclude retrospective valid_to and unknown future configurations.
CREATE FUNCTION acb_motor_v4_0_api.configuracion_asof(cutoff timestamptz)
RETURNS TABLE(configuration_id text,stand_id text,valid_from timestamptz,
 drive_version text,control_version text,sensor_version text,
 gear_ratio double precision,roll_radius_m double precision)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog AS $$
 SELECT DISTINCT ON (stand_id) configuration_id,stand_id,valid_from,
 drive_version,control_version,sensor_version,gear_ratio,roll_radius_m
 FROM acb_motor_v4_0.configuraciones WHERE known_at<=cutoff AND valid_from<=cutoff
 ORDER BY stand_id,valid_from DESC;
$$;
REVOKE ALL ON SCHEMA acb_motor_v4_0_api FROM PUBLIC;
REVOKE EXECUTE ON ALL FUNCTIONS IN SCHEMA acb_motor_v4_0_api FROM PUBLIC;
