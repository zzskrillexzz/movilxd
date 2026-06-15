-- ============================================================
-- MIGRACIÓN: Corrección de columnas faltantes en la BD
-- ============================================================
-- Ejecutar esto en SQLyog contra la base db_drogueria_sandiego
-- ============================================================

-- 1. t_pedido: Agregar columnas para tracking de pedidos
ALTER TABLE t_pedido
  ADD COLUMN ped_token_entrega VARCHAR(64) DEFAULT NULL AFTER ped_estado_pago,
  ADD COLUMN ped_notificado TINYINT(1) DEFAULT 0 AFTER ped_token_entrega,
  ADD COLUMN ped_factura_enviada TINYINT(1) DEFAULT 0 AFTER ped_notificado;

-- 2. t_devolucion: Agregar columna dev_com_id_fk (código la usa en vez de dev_ped_id_fk)
ALTER TABLE t_devolucion
  ADD COLUMN dev_com_id_fk VARCHAR(20) DEFAULT NULL AFTER dev_fecha;

-- 3. t_factura: Agregar columna fac_cli_id_fk si no existe
ALTER TABLE t_factura
  ADD COLUMN fac_cli_id_fk BIGINT(20) DEFAULT NULL AFTER fac_usu_id_fk;

-- 4. t_producto: Agregar columnas de presentación y laboratorio
ALTER TABLE t_producto
  ADD COLUMN pro_presentacion VARCHAR(100) DEFAULT NULL AFTER pro_prov_id_fk,
  ADD COLUMN pro_laboratorio VARCHAR(100) DEFAULT NULL AFTER pro_presentacion;

-- ============================================================
-- Verificación: listar las nuevas columnas
-- ============================================================
SELECT 't_pedido' AS tabla, COLUMN_NAME, COLUMN_TYPE 
FROM information_schema.COLUMNS 
WHERE TABLE_NAME = 't_pedido' 
  AND COLUMN_NAME IN ('ped_token_entrega','ped_notificado','ped_factura_enviada');

SELECT 't_devolucion' AS tabla, COLUMN_NAME, COLUMN_TYPE 
FROM information_schema.COLUMNS 
WHERE TABLE_NAME = 't_devolucion' 
  AND COLUMN_NAME IN ('dev_com_id_fk');

SELECT 't_factura' AS tabla, COLUMN_NAME, COLUMN_TYPE 
FROM information_schema.COLUMNS 
WHERE TABLE_NAME = 't_factura' 
  AND COLUMN_NAME IN ('fac_cli_id_fk');

SELECT 't_producto' AS tabla, COLUMN_NAME, COLUMN_TYPE 
FROM information_schema.COLUMNS 
WHERE TABLE_NAME = 't_producto' 
  AND COLUMN_NAME IN ('pro_presentacion','pro_laboratorio');
