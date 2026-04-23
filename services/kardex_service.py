from flask import current_app
from models.kardex_model import kardex

def listarKardex():
    c = current_app.mysql.connection.cursor()
    sql = """
        SELECT kar_id, kar_pro_id_fk, kar_lot_id_fk, kar_inm_id_fk, kar_fecha, kar_tipo, 
               kar_cantidad, kar_saldo_anterior, kar_saldo_actual, kar_costo_unitario, kar_costo_total 
        FROM t_kardex
    """
    c.execute(sql)
    datos = c.fetchall()
    lista = []
    for p in datos:
        k = kardex(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9], p[10]).todic()
        lista.append(k)
    return lista

def registrarKardex(KAR_ID, KAR_PRO_ID_FK, KAR_LOT_ID_FK, KAR_INM_ID_FK, KAR_FECHA, KAR_TIPO, KAR_CANTIDAD, KAR_SALDO_ANTERIOR, KAR_SALDO_ACTUAL, KAR_COSTO_UNITARIO, KAR_COSTO_TOTAL):
    c = current_app.mysql.connection.cursor()
    sql = """
        INSERT INTO t_kardex (kar_id, kar_pro_id_fk, kar_lot_id_fk, kar_inm_id_fk, kar_fecha, kar_tipo, 
                              kar_cantidad, kar_saldo_anterior, kar_saldo_actual, kar_costo_unitario, kar_costo_total) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    c.execute(sql, (KAR_ID, KAR_PRO_ID_FK, KAR_LOT_ID_FK, KAR_INM_ID_FK, KAR_FECHA, KAR_TIPO, KAR_CANTIDAD, KAR_SALDO_ANTERIOR, KAR_SALDO_ACTUAL, KAR_COSTO_UNITARIO, KAR_COSTO_TOTAL))
    current_app.mysql.connection.commit()
    id = c.lastrowid
    c.close()
    return kardex(KAR_ID, KAR_PRO_ID_FK, KAR_LOT_ID_FK, KAR_INM_ID_FK, KAR_FECHA, KAR_TIPO, KAR_CANTIDAD, KAR_SALDO_ANTERIOR, KAR_SALDO_ACTUAL, KAR_COSTO_UNITARIO, KAR_COSTO_TOTAL).todic()

def editarKardex(KAR_ID, KAR_PRO_ID_FK, KAR_LOT_ID_FK, KAR_INM_ID_FK, KAR_FECHA, KAR_TIPO,
                 KAR_CANTIDAD, KAR_SALDO_ANTERIOR, KAR_SALDO_ACTUAL, KAR_COSTO_UNITARIO, KAR_COSTO_TOTAL):
    c = current_app.mysql.connection.cursor()
    sql = """
        UPDATE t_kardex
        SET kar_pro_id_fk=%s, kar_lot_id_fk=%s, kar_inm_id_fk=%s, kar_fecha=%s, kar_tipo=%s,
            kar_cantidad=%s, kar_saldo_anterior=%s, kar_saldo_actual=%s,
            kar_costo_unitario=%s, kar_costo_total=%s
        WHERE kar_id=%s
    """
    c.execute(sql, (KAR_PRO_ID_FK, KAR_LOT_ID_FK, KAR_INM_ID_FK, KAR_FECHA, KAR_TIPO,
                    KAR_CANTIDAD, KAR_SALDO_ANTERIOR, KAR_SALDO_ACTUAL,
                    KAR_COSTO_UNITARIO, KAR_COSTO_TOTAL, KAR_ID))
    current_app.mysql.connection.commit()
    filas = c.rowcount
    c.close()
    if filas == 0:
        return None
    return kardex(KAR_ID, KAR_PRO_ID_FK, KAR_LOT_ID_FK, KAR_INM_ID_FK, KAR_FECHA, KAR_TIPO,
                  KAR_CANTIDAD, KAR_SALDO_ANTERIOR, KAR_SALDO_ACTUAL,
                  KAR_COSTO_UNITARIO, KAR_COSTO_TOTAL).todic()


def eliminarKardex(KAR_ID):
    c = current_app.mysql.connection.cursor()
    c.execute("DELETE FROM t_kardex WHERE kar_id=%s", (KAR_ID,))
    current_app.mysql.connection.commit()
    filas = c.rowcount
    c.close()
    return filas > 0


def buscarKardex(KAR_ID):
    c = current_app.mysql.connection.cursor()
    c.execute("""
        SELECT kar_id, kar_pro_id_fk, kar_lot_id_fk, kar_inm_id_fk, kar_fecha, kar_tipo,
               kar_cantidad, kar_saldo_anterior, kar_saldo_actual, kar_costo_unitario, kar_costo_total
        FROM t_kardex WHERE kar_id=%s
    """, (KAR_ID,))
    r = c.fetchone()
    c.close()
    if not r:
        return None
    return kardex(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10]).todic()