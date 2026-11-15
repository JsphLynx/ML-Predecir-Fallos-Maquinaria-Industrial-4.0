-- Reproducir conocimiento en un instante. No concede acceso a tablas completas.
CREATE SCHEMA acb_motor_v3_1_api;
CREATE FUNCTION acb_motor_v3_1_api.features_asof(cutoff timestamptz)
RETURNS SETOF acb_motor_v3_1.features LANGUAGE sql STABLE SECURITY DEFINER
SET search_path=pg_catalog AS $$
 SELECT f.* FROM acb_motor_v3_1.features f WHERE f.timestamp<=cutoff;
$$;
CREATE FUNCTION acb_motor_v3_1_api.planes_asof(cutoff timestamptz)
RETURNS SETOF acb_motor_v3_1.plan_mantenimiento LANGUAGE sql STABLE SECURITY DEFINER
SET search_path=pg_catalog AS $$
 SELECT DISTINCT ON (run_id,plan_id) p.* FROM acb_motor_v3_1.plan_mantenimiento p
 WHERE known_at<=cutoff ORDER BY run_id,plan_id,known_at DESC,revision DESC;
$$;
CREATE FUNCTION acb_motor_v3_1_api.servicios_asof(cutoff timestamptz)
RETURNS TABLE(run_id text,maintenance_id text,asset_id text,start timestamptz,kind text,
 completed_end timestamptz,action text,completed_operating_hours double precision)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog AS $$
 SELECT run_id,maintenance_id,asset_id,start,kind,
 CASE WHEN result_available_at<=cutoff THEN "end" END,
 CASE WHEN result_available_at<=cutoff THEN action END,
 CASE WHEN result_available_at<=cutoff THEN completed_operating_hours END
 FROM acb_motor_v3_1.mantenimiento WHERE known_at<=cutoff;
$$;
REVOKE ALL ON SCHEMA acb_motor_v3_1_api FROM PUBLIC;
REVOKE EXECUTE ON ALL FUNCTIONS IN SCHEMA acb_motor_v3_1_api FROM PUBLIC;
