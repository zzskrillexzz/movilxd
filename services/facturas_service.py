from flask import current_app
from models.facturas_model import facturas

def listarFacturas():
    c = current_app.mysql.connection.cursor()
    sql = "SELECT fac_id, fac_fecha_emision, fac_email_enviado, fac_forma_pago, fac_cuenta_bancaria, fac_total, fac_usu_id_fk, fac_estado FROM t_factura"
    c.execute(sql)
    reg = c.fetchall()
    lista = []
    for f_row in reg:
        fac = facturas(
            id=f_row[0], fecha_emision=f_row[1], email_enviado=f_row[2],
            forma_pago=f_row[3], cuenta_bancaria=f_row[4], total=f_row[5],
            usuario_id=f_row[6], fac_estado=f_row[7]
        ).todic()
        lista.append(fac)
    return lista

def registrarFacturas(data):
    try:
        cursor = current_app.mysql.connection.cursor()
        sql = """
            INSERT INTO t_factura (fac_id, fac_fecha_emision, fac_email_enviado, fac_forma_pago, fac_cuenta_bancaria, fac_total, fac_usu_id_fk, fac_estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            data.get('id'),
            data.get('fecha_emision'),
            data.get('email_enviado', 0),
            data.get('forma_pago'),
            data.get('cuenta_bancaria') or data.get('fac_cuenta_bancaria'),
            data.get('total'),
            data.get('usuario_id'),
            data.get('estado', 'Vigente')
        ))
        current_app.mysql.connection.commit()
        cursor.close()
        return {"mensaje": "Factura registrada correctamente"}
    except Exception as e:
        raise e

def editarFacturas(fac_id, data):
    try:
        cursor = current_app.mysql.connection.cursor()
        sql = """
            UPDATE t_factura SET fac_fecha_emision=%s, fac_email_enviado=%s, fac_forma_pago=%s,
            fac_cuenta_bancaria=%s, fac_total=%s, fac_usu_id_fk=%s, fac_estado=%s WHERE fac_id=%s
        """
        cursor.execute(sql, (
            data.get('fecha_emision'), data.get('email_enviado'), data.get('forma_pago'),
            data.get('cuenta_bancaria') or data.get('fac_cuenta_bancaria'),
            data.get('total'), data.get('usuario_id'), data.get('estado'), fac_id
        ))
        current_app.mysql.connection.commit()
        cursor.close()
        return {"mensaje": "Factura actualizada correctamente"}
    except Exception as e:
        raise e

def eliminarFacturas(fac_id):
    try:
        cursor = current_app.mysql.connection.cursor()
        sql = "DELETE FROM t_factura WHERE fac_id = %s"
        cursor.execute(sql, (fac_id,))
        current_app.mysql.connection.commit()
        cursor.close()
        return {"mensaje": "Factura eliminada correctamente"}
    except Exception as e:
        raise e

def buscarFacturas(fac_id):
    try:
        cursor = current_app.mysql.connection.cursor()
        sql = "SELECT fac_id, fac_fecha_emision, fac_email_enviado, fac_forma_pago, fac_cuenta_bancaria, fac_total, fac_usu_id_fk, fac_estado FROM t_factura WHERE fac_id = %s"
        cursor.execute(sql, (fac_id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return facturas(id=row[0], fecha_emision=row[1], email_enviado=row[2],
                          forma_pago=row[3], cuenta_bancaria=row[4], total=row[5],
                          usuario_id=row[6], fac_estado=row[7]).todic()
        return None
    except Exception as e:
        raise e
