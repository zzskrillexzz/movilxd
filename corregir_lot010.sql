-- ============================================================
-- CORREGIR lot_numero de TODOS los lotes según su producto
-- ============================================================
-- Uso: mysql -u root -p db_drogueria_sandiego < corregir_lot010.sql
-- ============================================================

START TRANSACTION;

-- 1. Crear tabla temporal con el nuevo número calculado
CREATE TEMPORARY TABLE _correccion AS
SELECT 
  l.lot_id,
  CONCAT(
    'LT-',
    UPPER(LEFT(p.pro_nombre, 3)),
    '-',
    YEAR(l.lot_fecha_vencimiento),
    '-',
    LPAD(
      (SELECT COUNT(*) + 1 
       FROM t_lote l2 
       JOIN t_producto p2 ON l2.lot_pro_id_fk = p2.pro_id
       WHERE p2.pro_id = p.pro_id 
         AND YEAR(l2.lot_fecha_vencimiento) = YEAR(l.lot_fecha_vencimiento)
         AND l2.lot_id < l.lot_id),
      3, '0'
    )
  ) AS nuevo_numero
FROM t_lote l
JOIN t_producto p ON l.lot_pro_id_fk = p.pro_id
ORDER BY l.lot_pro_id_fk, l.lot_id ASC;

-- 2. Aplicar la corrección
UPDATE t_lote l
JOIN _correccion c ON l.lot_id = c.lot_id
SET l.lot_numero = c.nuevo_numero;

-- 3. Limpiar
DROP TEMPORARY TABLE _correccion;

COMMIT;

-- 4. Mostrar resultado
SELECT lot_id, lot_pro_id_fk, lot_numero FROM t_lote ORDER BY lot_id;
