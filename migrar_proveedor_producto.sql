-- ============================================================
-- Migración: Copia datos de pro_prov_id_fk (t_producto) a
--            t_proveedor_producto (nueva tabla relacional)
-- ============================================================
-- Ejecutar: mysql -u root -h localhost -P 3307 db_drogueria_sandiego < migrar_proveedor_producto.sql
-- ============================================================

-- 1. Agregar UNIQUE KEY para evitar duplicados
ALTER TABLE t_proveedor_producto ADD UNIQUE KEY IF NOT EXISTS uq_prov_prod (ppp_prov_id_fk, ppp_pro_id_fk);

-- 2. Migrar datos desde la columna antigua pro_prov_id_fk
INSERT IGNORE INTO t_proveedor_producto (ppp_prov_id_fk, ppp_pro_id_fk)
SELECT DISTINCT pro_prov_id_fk, pro_id
FROM t_producto
WHERE pro_prov_id_fk IS NOT NULL
  AND TRIM(pro_prov_id_fk) != '';

-- 3. Verificar resultado
SELECT CONCAT('Migración completada. Total registros: ', COUNT(*)) AS info FROM t_proveedor_producto;
