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

def editarKardex():
    return

def eliminarKardex():
    return

def buscarKardex():
    return