-- ================================================================
-- MIGRACIÓN: Corrección de bugs QA — Distribuidora SANDIEGO
-- ================================================================
-- BUG-004: Agregar columnas faltantes en t_pedido
-- BUG-005: Agregar columna faltante en t_factura  
-- BUG-006: Desactivar trigger que duplica lógica de stock
-- ================================================================

USE `db_drogueria_sandiego`;

-- ── BUG-004: Columnas faltantes en t_pedido ──
ALTER TABLE `t_pedido`
  ADD COLUMN IF NOT EXISTS `ped_token_entrega` VARCHAR(100) DEFAULT NULL COMMENT 'Token único para confirmación de entrega QR' AFTER `ped_usu_id_fk`,
  ADD COLUMN IF NOT EXISTS `ped_notificado` TINYINT(1) DEFAULT 0 COMMENT '1=Cliente notificado / 0=No notificado' AFTER `ped_token_entrega`,
  ADD COLUMN IF NOT EXISTS `ped_factura_enviada` TINYINT(1) DEFAULT 0 COMMENT '1=Factura enviada / 0=No enviada' AFTER `ped_notificado`;

-- ── BUG-005: Columna faltante en t_factura ──
ALTER TABLE `t_factura`
  ADD COLUMN IF NOT EXISTS `fac_cli_id_fk` BIGINT(20) DEFAULT NULL COMMENT 'ID del cliente asociado a la factura' AFTER `fac_usu_id_fk`,
  ADD KEY IF NOT EXISTS `fac_cli_id_fk` (`fac_cli_id_fk`);

-- ── BUG-006: Eliminar trigger que duplica descuento de stock ──
-- El trigger trg_monitoria_after_movimiento actualiza pro_cantidad_disponible
-- e inserta en t_monitoria. El backend Python hace exactamente lo mismo
-- desde detalles_pedidos_service.py, pedidos_service.py, devoluciones_service.py
-- Esto causa DOBLE descuento de stock y registros duplicados en t_monitoria.
DROP TRIGGER IF EXISTS `trg_monitoria_after_movimiento`;

SELECT '✅ Migración completada — columnas agregadas, trigger eliminado' AS resultado;
