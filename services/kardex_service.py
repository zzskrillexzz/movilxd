from flask import current_app
from models.kardex_model import kardex

def listarKardex():
    try:
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
        c.close()
        return lista
    except Exception as e:
        print(f"Error en listarKardex: {e}")
        return []

def registrarKardex(KAR_ID, KAR_PRO_ID_FK, KAR_LOT_ID_FK, KAR_INM_ID_FK, KAR_FECHA, KAR_TIPO, 
                    KAR_CANTIDAD, KAR_SALDO_ANTERIOR, KAR_SALDO_ACTUAL, KAR_COSTO_UNITARIO, KAR_COSTO_TOTAL):
    try:
        c = current_app.mysql.connection.cursor()
        sql = """
            INSERT INTO t_kardex (kar_id, kar_pro_id_fk, kar_lot_id_fk, kar_inm_id_fk, kar_fecha, kar_tipo, 
                                  kar_cantidad, kar_saldo_anterior, kar_saldo_actual, kar_costo_unitario, kar_costo_total) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        c.execute(sql, (KAR_ID, KAR_PRO_ID_FK, KAR_LOT_ID_FK, KAR_INM_ID_FK, KAR_FECHA, KAR_TIPO, 
                       KAR_CANTIDAD, KAR_SALDO_ANTERIOR, KAR_SALDO_ACTUAL, KAR_COSTO_UNITARIO, KAR_COSTO_TOTAL))
        current_app.mysql.connection.commit()
        c.close()
        return kardex(KAR_ID, KAR_PRO_ID_FK, KAR_LOT_ID_FK, KAR_INM_ID_FK, KAR_FECHA, KAR_TIPO, 
                     KAR_CANTIDAD, KAR_SALDO_ANTERIOR, KAR_SALDO_ACTUAL, KAR_COSTO_UNITARIO, KAR_COSTO_TOTAL).todic()
    except Exception as e:
        print(f"Error en registrarKardex: {e}")
        return None

def editarKardex(id, KAR_PRO_ID_FK, KAR_LOT_ID_FK, KAR_INM_ID_FK, KAR_FECHA, KAR_TIPO, 
                KAR_CANTIDAD, KAR_SALDO_ANTERIOR, KAR_SALDO_ACTUAL, KAR_COSTO_UNITARIO, KAR_COSTO_TOTAL):
    try:
        c = current_app.mysql.connection.cursor()
        sql = """
            UPDATE t_kardex 
            SET kar_pro_id_fk = %s, kar_lot_id_fk = %s, kar_inm_id_fk = %s, 
                kar_fecha = %s, kar_tipo = %s, kar_cantidad = %s, 
                kar_saldo_anterior = %s, kar_saldo_actual = %s, 
                kar_costo_unitario = %s, kar_costo_total = %s
            WHERE kar_id = %s
        """
        c.execute(sql, (KAR_PRO_ID_FK, KAR_LOT_ID_FK, KAR_INM_ID_FK, KAR_FECHA, KAR_TIPO, 
                       KAR_CANTIDAD, KAR_SALDO_ANTERIOR, KAR_SALDO_ACTUAL, 
                       KAR_COSTO_UNITARIO, KAR_COSTO_TOTAL, id))
        current_app.mysql.connection.commit()
        afectadas = c.rowcount
        c.close()
        
        if afectadas > 0:
            return buscarKardex(id)
        return None
    except Exception as e:
        print(f"Error en editarKardex: {e}")
        return None

def eliminarKardex(id):
    try:
        c = current_app.mysql.connection.cursor()
        sql = "DELETE FROM t_kardex WHERE kar_id = %s"
        c.execute(sql, (id,))
        current_app.mysql.connection.commit()
        afectadas = c.rowcount
        c.close()
        return afectadas > 0
    except Exception as e:
        print(f"Error en eliminarKardex: {e}")
        return False

def buscarKardex(kar_id=None):
    try:
        c = current_app.mysql.connection.cursor()
        if kar_id:
            sql = """
                SELECT kar_id, kar_pro_id_fk, kar_lot_id_fk, kar_inm_id_fk, kar_fecha, kar_tipo, 
                       kar_cantidad, kar_saldo_anterior, kar_saldo_actual, kar_costo_unitario, kar_costo_total 
                FROM t_kardex 
                WHERE kar_id = %s
            """
            c.execute(sql, (kar_id,))
            resultado = c.fetchone()
            c.close()
            if resultado:
                return {
                    "kar_id": resultado[0],
                    "kar_pro_id_fk": resultado[1],
                    "kar_lot_id_fk": resultado[2],
                    "kar_inm_id_fk": resultado[3],
                    "kar_fecha": resultado[4],
                    "kar_tipo": resultado[5],
                    "kar_cantidad": resultado[6],
                    "kar_saldo_anterior": resultado[7],
                    "kar_saldo_actual": resultado[8],
                    "kar_costo_unitario": resultado[9],
                    "kar_costo_total": resultado[10]
                }
            return None
        else:
            # Si no se pasa id, retorna todos los registros
            sql = """
                SELECT kar_id, kar_pro_id_fk, kar_lot_id_fk, kar_inm_id_fk, kar_fecha, kar_tipo, 
                       kar_cantidad, kar_saldo_anterior, kar_saldo_actual, kar_costo_unitario, kar_costo_total 
                FROM t_kardex
            """
            c.execute(sql)
            datos = c.fetchall()
            lista = []
            for p in datos:
                k = {
                    "kar_id": p[0],
                    "kar_pro_id_fk": p[1],
                    "kar_lot_id_fk": p[2],
                    "kar_inm_id_fk": p[3],
                    "kar_fecha": p[4],
                    "kar_tipo": p[5],
                    "kar_cantidad": p[6],
                    "kar_saldo_anterior": p[7],
                    "kar_saldo_actual": p[8],
                    "kar_costo_unitario": p[9],
                    "kar_costo_total": p[10]
                }
                lista.append(k)
            c.close()
            return lista
    except Exception as e:
        print(f"Error en buscarKardex: {e}")
        return None if kar_id else []