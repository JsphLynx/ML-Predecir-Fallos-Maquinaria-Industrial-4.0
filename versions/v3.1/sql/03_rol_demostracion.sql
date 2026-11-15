-- Ejecutar una vez, en una base de pruebas y con permiso de crear roles.
-- Sin LOGIN ni credenciales; un administrador asigna este rol a un usuario lector.
CREATE ROLE acb_v31_demo_reader NOLOGIN;
GRANT USAGE ON SCHEMA acb_motor_v3_1_api TO acb_v31_demo_reader;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA acb_motor_v3_1_api TO acb_v31_demo_reader;
-- No acceso directo a datos, targets, verdad, ni resultados futuros de mantenimiento.
