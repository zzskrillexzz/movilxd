-- ============================================================
-- MIGRACIÓN: Renumerar lotes secuencialmente
-- ============================================================
-- Uso: mysql -u root -p db_drogueria_sandiego < migracion_renumerar_lotes.sql
-- ============================================================

START TRANSACTION;

-- 1. Deshabilitar chequeo de FK temporalmente
SET FOREIGN_KEY_CHECKS = 0;

-- 2. Crear tabla temporal con el mapeo old_id → new_id
DROP TABLE IF EXISTS _tmp_renum_lotes;
CREATE TEMPORARY TABLE _tmp_renum_lotes (
  old_id VARCHAR(20) NOT NULL PRIMARY KEY,
  new_id VARCHAR(20) NOT NULL
);

-- 3. Insertar el mapeo: ordenado por número actual, asigna nuevo secuencial
INSERT INTO _tmp_renum_lotes (old_id, new_id)
SELECT 
  lot_id,
  CONCAT('LOT', LPAD(@rownum := @rownum + 1, 3, '0')) AS new_id
FROM t_lote, (SELECT @rownum := 0) AS r
ORDER BY CAST(SUBSTRING(lot_id, 4) AS UNSIGNED) ASC;

-- 4. Mostrar el mapeo (solo para verificar)
SELECT 'Mapeo de IDs:' AS '---';
SELECT old_id, new_id FROM _tmp_renum_lotes ORDER BY new_id;

-- ============================================================
-- 5. Actualizar t_lote
-- ============================================================
UPDATE t_lote l
INNER JOIN _tmp_renum_lotes tmp ON l.lot_id = tmp.old_id
SET l.lot_id = tmp.new_id;

-- ============================================================
-- 6. Actualizar t_alerta_vencimiento
-- ============================================================
UPDATE t_alerta_vencimiento a
INNER JOIN _tmp_renum_lotes tmp ON a.alv_lot_id_fk = tmp.old_id
SET a.alv_lot_id_fk = tmp.new_id;

-- ============================================================
-- 7. Actualizar t_detalle_compra
-- ============================================================
UPDATE t_detalle_compra dc
INNER JOIN _tmp_renum_lotes tmp ON dc.dco_lot_id_fk = tmp.old_id
SET dc.dco_lot_id_fk = tmp.new_id;

-- ============================================================
-- 8. Actualizar t_inventario_movimiento
-- ============================================================
UPDATE t_inventario_movimiento inv
INNER JOIN _tmp_renum_lotes tmp ON inv.inm_lot_id_fk = tmp.old_id
SET inv.inm_lot_id_fk = tmp.new_id;

-- ============================================================
-- 9. Actualizar t_monitoria
-- ============================================================
UPDATE t_monitoria m
INNER JOIN _tmp_renum_lotes tmp ON m.mon_lot_id_fk = tmp.old_id
SET m.mon_lot_id_fk = tmp.new_id;

-- ============================================================
-- 10. Actualizar t_detalle_pedido (si tiene columna det_lot_id_fk)
-- ============================================================
UPDATE t_detalle_pedido dp
INNER JOIN _tmp_renum_lotes tmp ON dp.det_lot_id_fk = tmp.old_id
SET dp.det_lot_id_fk = tmp.new_id;

-- ============================================================
-- 11. Actualizar t_devolucion (si tiene columna dev_lot_id_fk)
-- ============================================================
UPDATE t_devolucion d
INNER JOIN _tmp_renum_lotes tmp ON d.dev_lot_id_fk = tmp.old_id
SET d.dev_lot_id_fk = tmp.new_id;

-- ============================================================
-- 12. Limpiar
-- ============================================================
DROP TEMPORARY TABLE IF EXISTS _tmp_renum_lotes;

-- Re-habilitar FK checks
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
COMMIT;

-- Mostrar resultado
SELECT 'Migración completada. Nuevos IDs de lotes:' AS '---';
SELECT lot_id, lot_numero, lot_pro_id_fk FROM t_lote ORDER BY lot_id;
