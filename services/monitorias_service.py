from flask import current_app
from models.monitorias_model import monitoria

def listarMonitoria(limit=None, offset=None, tipo=None, fecha_desde=None, fecha_hasta=None, q=None):
    try:
        c = current_app.mysql.connection.cursor()

        # ── Consulta de total (sin filtros para contar) ──
        count_sql = "SELECT COUNT(*) FROM t_monitoria"
        count_params = []

        # ── Consulta de datos ──
        sql = """
            SELECT mon_id, mon_pro_id_fk, mon_lot_id_fk, mon_inm_id_fk, mon_fecha, mon_tipo,
                   mon_cantidad, mon_saldo_anterior, mon_saldo_actual, mon_costo_unitario, mon_costo_total
            FROM t_monitoria
        """
        where_clauses = []
        params = []

        if q:
            where_clauses.append("(mon_id LIKE %s OR mon_pro_id_fk LIKE %s)")
            q_param = f"%{q}%"
            params.append(q_param)
            params.append(q_param)
        if tipo:
            where_clauses.append("mon_tipo = %s")
            params.append(tipo)
        if fecha_desde:
            where_clauses.append("mon_fecha >= %s")
            params.append(fecha_desde)
        if fecha_hasta:
            where_clauses.append("mon_fecha <= %s")
            params.append(fecha_hasta)

        if where_clauses:
            where = " WHERE " + " AND ".join(where_clauses)
            sql += where
            count_sql += where
            count_params = params.copy()

        sql += " ORDER BY mon_fecha DESC, mon_id DESC"

        if limit is not None:
            sql += " LIMIT %s"
            params.append(limit)
        if offset is not None:
            sql += " OFFSET %s"
            params.append(offset)

        # Total de registros (sin paginación)
        c.execute(count_sql, tuple(count_params))
        total = c.fetchone()[0]

        # Datos paginados
        c.execute(sql, tuple(params))
        datos = c.fetchall()

        lista = []
        for p in datos:
            m = monitoria(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9], p[10]).todic()
            lista.append(m)
        c.close()

        return {"data": lista, "total": total}
    except Exception as e:
        print(f"Error en listarMonitoria: {e}")
        return {"data": [], "total": 0}

def registrarMonitoria(MON_ID, MON_PRO_ID_FK, MON_LOT_ID_FK, MON_INM_ID_FK, MON_FECHA, MON_TIPO, 
                       MON_CANTIDAD, MON_SALDO_ANTERIOR, MON_SALDO_ACTUAL, MON_COSTO_UNITARIO, MON_COSTO_TOTAL):
    try:
        c = current_app.mysql.connection.cursor()
        sql = """
            INSERT INTO t_monitoria (mon_id, mon_pro_id_fk, mon_lot_id_fk, mon_inm_id_fk, mon_fecha, mon_tipo, 
                                     mon_cantidad, mon_saldo_anterior, mon_saldo_actual, mon_costo_unitario, mon_costo_total) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        c.execute(sql, (MON_ID, MON_PRO_ID_FK, MON_LOT_ID_FK, MON_INM_ID_FK, MON_FECHA, MON_TIPO, 
                       MON_CANTIDAD, MON_SALDO_ANTERIOR, MON_SALDO_ACTUAL, MON_COSTO_UNITARIO, MON_COSTO_TOTAL))
        current_app.mysql.connection.commit()
        c.close()
        return monitoria(MON_ID, MON_PRO_ID_FK, MON_LOT_ID_FK, MON_INM_ID_FK, MON_FECHA, MON_TIPO, 
                         MON_CANTIDAD, MON_SALDO_ANTERIOR, MON_SALDO_ACTUAL, MON_COSTO_UNITARIO, MON_COSTO_TOTAL).todic()
    except Exception as e:
        print(f"Error en registrarMonitoria: {e}")
        return None

def editarMonitoria(id, MON_PRO_ID_FK, MON_LOT_ID_FK, MON_INM_ID_FK, MON_FECHA, MON_TIPO, 
                    MON_CANTIDAD, MON_SALDO_ANTERIOR, MON_SALDO_ACTUAL, MON_COSTO_UNITARIO, MON_COSTO_TOTAL):
    try:
        c = current_app.mysql.connection.cursor()
        sql = """
            UPDATE t_monitoria 
            SET mon_pro_id_fk = %s, mon_lot_id_fk = %s, mon_inm_id_fk = %s, 
                mon_fecha = %s, mon_tipo = %s, mon_cantidad = %s, 
                mon_saldo_anterior = %s, mon_saldo_actual = %s, 
                mon_costo_unitario = %s, mon_costo_total = %s
            WHERE mon_id = %s
        """
        c.execute(sql, (MON_PRO_ID_FK, MON_LOT_ID_FK, MON_INM_ID_FK, MON_FECHA, MON_TIPO, 
                       MON_CANTIDAD, MON_SALDO_ANTERIOR, MON_SALDO_ACTUAL, 
                       MON_COSTO_UNITARIO, MON_COSTO_TOTAL, id))
        current_app.mysql.connection.commit()
        afectadas = c.rowcount
        c.close()
        
        if afectadas > 0:
            return buscarMonitoria(id)
        return None
    except Exception as e:
        print(f"Error en editarMonitoria: {e}")
        return None

def eliminarMonitoria(id):
    try:
        c = current_app.mysql.connection.cursor()
        sql = "DELETE FROM t_monitoria WHERE mon_id = %s"
        c.execute(sql, (id,))
        current_app.mysql.connection.commit()
        afectadas = c.rowcount
        c.close()
        return afectadas > 0
    except Exception as e:
        print(f"Error en eliminarMonitoria: {e}")
        return False

def buscarMonitoria(mon_id=None):
    try:
        c = current_app.mysql.connection.cursor()
        if mon_id:
            sql = """
                SELECT mon_id, mon_pro_id_fk, mon_lot_id_fk, mon_inm_id_fk, mon_fecha, mon_tipo, 
                       mon_cantidad, mon_saldo_anterior, mon_saldo_actual, mon_costo_unitario, mon_costo_total 
                FROM t_monitoria 
                WHERE mon_id = %s
            """
            c.execute(sql, (mon_id,))
            resultado = c.fetchone()
            c.close()
            if resultado:
                return {
                    "mon_id": resultado[0],
                    "mon_pro_id_fk": resultado[1],
                    "mon_lot_id_fk": resultado[2],
                    "mon_inm_id_fk": resultado[3],
                    "mon_fecha": str(resultado[4]) if resultado[4] else None,
                    "mon_tipo": resultado[5],
                    "mon_cantidad": resultado[6],
                    "mon_saldo_anterior": resultado[7],
                    "mon_saldo_actual": resultado[8],
                    "mon_costo_unitario": float(resultado[9]) if resultado[9] else None,
                    "mon_costo_total": float(resultado[10]) if resultado[10] else None
                }
            return None
        else:
            sql = """
                SELECT mon_id, mon_pro_id_fk, mon_lot_id_fk, mon_inm_id_fk, mon_fecha, mon_tipo, 
                       mon_cantidad, mon_saldo_anterior, mon_saldo_actual, mon_costo_unitario, mon_costo_total 
                FROM t_monitoria
            """
            c.execute(sql)
            datos = c.fetchall()
            lista = []
            for p in datos:
                m = {
                    "mon_id": p[0],
                    "mon_pro_id_fk": p[1],
                    "mon_lot_id_fk": p[2],
                    "mon_inm_id_fk": p[3],
                    "mon_fecha": str(p[4]) if p[4] else None,
                    "mon_tipo": p[5],
                    "mon_cantidad": p[6],
                    "mon_saldo_anterior": p[7],
                    "mon_saldo_actual": p[8],
                    "mon_costo_unitario": float(p[9]) if p[9] else None,
                    "mon_costo_total": float(p[10]) if p[10] else None
                }
                lista.append(m)
            c.close()
            return lista
    except Exception as e:
        print(f"Error en buscarMonitoria: {e}")
        return None if mon_id else []