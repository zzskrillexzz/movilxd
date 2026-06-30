import MySQLdb
conn = MySQLdb.connect(host='localhost', user='root', port=3307, db='db_drogueria_sandiego')
c = conn.cursor()
c.execute('DROP TRIGGER IF EXISTS trg_monitoria_after_movimiento')

trigger_sql = """
CREATE TRIGGER trg_monitoria_after_movimiento
AFTER INSERT ON t_inventario_movimiento
FOR EACH ROW
BEGIN
    DECLARE v_saldo_anterior INT;
    DECLARE v_saldo_actual INT;
    DECLARE v_costo DECIMAL(12,2);
    DECLARE v_nuevo_id VARCHAR(20);
    SET v_nuevo_id = CONCAT('MON', DATE_FORMAT(NOW(), '%y%m%d%H%i%s'), FLOOR(RAND() * 99));
    SELECT COALESCE(SUM(lot_cantidad_actual), 0), COALESCE(AVG(pro_precio), 0)
    INTO v_saldo_anterior, v_costo
    FROM t_lote l
    JOIN t_producto p ON p.pro_id = l.lot_pro_id_fk
    WHERE l.lot_pro_id_fk = NEW.inm_pro_id_fk;
    IF NEW.inm_tipo_movimiento = 'Entrada' THEN
        SET v_saldo_actual = v_saldo_anterior + NEW.inm_cantidad;
    ELSEIF NEW.inm_tipo_movimiento = 'Salida' THEN
        SET v_saldo_actual = v_saldo_anterior - NEW.inm_cantidad;
    ELSE
        SET v_saldo_actual = v_saldo_anterior + NEW.inm_cantidad;
    END IF;
    INSERT INTO t_monitoria (mon_id, mon_pro_id_fk, mon_lot_id_fk, mon_inm_id_fk,
        mon_fecha, mon_tipo, mon_cantidad, mon_saldo_anterior,
        mon_saldo_actual, mon_costo_unitario, mon_costo_total)
    VALUES (
        v_nuevo_id, NEW.inm_pro_id_fk, NEW.inm_lot_id_fk, NEW.inm_id,
        NEW.inm_fecha, NEW.inm_tipo_movimiento, NEW.inm_cantidad,
        v_saldo_anterior, v_saldo_actual, v_costo, NEW.inm_cantidad * v_costo
    );
END
"""
c.execute(trigger_sql)
conn.commit()
print('Trigger recreado correctamente')
c.close()
conn.close()
