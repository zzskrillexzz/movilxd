from flask import current_app
from models.compras_model import compras
import base64

def listarCompras():
    c = current_app.mysql.connection.cursor()
    sql = """
        SELECT c.com_id, c.com_fecha, c.com_prov_id_fk, c.com_usu_id_fk, c.com_total, c.com_estado, c.com_observacion,
               c.com_comprobante_tipo
        FROM t_compra c
    """
    c.execute(sql)
    datos = c.fetchall()
    
    lista = []
    for x in datos:
        tiene_comprobante = x[7] is not None
        com = compras(x[0], x[1], x[2], x[3], x[4], x[5], x[6], None, x[7]).todic()
        com['comp_tiene_comprobante'] = tiene_comprobante
        lista.append(com)
    return lista

def registrarCompras(COM_ID, COM_FECHA, COM_PROV_ID_FK, COM_USU_ID_FK, COM_TOTAL, COM_ESTADO, COM_OBSERVACION, COM_COMPROBANTE=None, COM_COMPROBANTE_TIPO=None):
    c = current_app.mysql.connection.cursor()
    comprobante_bin = None
    if COM_COMPROBANTE:
        comprobante_bin = base64.b64decode(COM_COMPROBANTE)
    sql = """
        INSERT INTO t_compra (com_id, com_fecha, com_prov_id_fk, com_usu_id_fk, com_total, com_estado, com_observacion, com_comprobante, com_comprobante_tipo) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    c.execute(sql, (COM_ID, COM_FECHA, COM_PROV_ID_FK, COM_USU_ID_FK, COM_TOTAL, COM_ESTADO, COM_OBSERVACION, comprobante_bin, COM_COMPROBANTE_TIPO))
    current_app.mysql.connection.commit()
    c.close()
    return compras(COM_ID, COM_FECHA, COM_PROV_ID_FK, COM_USU_ID_FK, COM_TOTAL, COM_ESTADO, COM_OBSERVACION, comprobante_bin, COM_COMPROBANTE_TIPO).todic()

def buscarCompras(COM_ID):
    c = current_app.mysql.connection.cursor()
    sql = "SELECT com_id, com_fecha, com_prov_id_fk, com_usu_id_fk, com_total, com_estado, com_observacion, com_comprobante, com_comprobante_tipo FROM t_compra WHERE com_id = %s"
    c.execute(sql, (COM_ID,))
    dato = c.fetchone()
    if dato:
        return compras(dato[0], dato[1], dato[2], dato[3], dato[4], dato[5], dato[6], dato[7], dato[8]).todic()
    return None

def editarCompras(COM_ID, data):
    c = current_app.mysql.connection.cursor()
    
    if 'com_comprobante' in data:
        comprobante_bin = None
        if data['com_comprobante']:
            comprobante_bin = base64.b64decode(data['com_comprobante'])
        sql = """
            UPDATE t_compra 
            SET com_fecha = %s, com_prov_id_fk = %s, com_usu_id_fk = %s, 
                com_total = %s, com_estado = %s, com_observacion = %s,
                com_comprobante = %s, com_comprobante_tipo = %s
            WHERE com_id = %s
        """
        c.execute(sql, (
            data.get('com_fecha'), data.get('com_prov_id_fk'), data.get('com_usu_id_fk'),
            data.get('com_total'), data.get('com_estado'), data.get('com_observacion'),
            comprobante_bin, data.get('com_comprobante_tipo'), COM_ID
        ))
    else:
        sql = """
            UPDATE t_compra 
            SET com_fecha = %s, com_prov_id_fk = %s, com_usu_id_fk = %s, 
                com_total = %s, com_estado = %s, com_observacion = %s
            WHERE com_id = %s
        """
        c.execute(sql, (
            data.get('com_fecha'), data.get('com_prov_id_fk'), data.get('com_usu_id_fk'),
            data.get('com_total'), data.get('com_estado'), data.get('com_observacion'), COM_ID
        ))
    
    current_app.mysql.connection.commit()
    c.close()
    return {"mensaje": "Compra actualizada correctamente"}

def eliminarCompras(COM_ID):
    c = current_app.mysql.connection.cursor()
    c.execute("DELETE FROM t_compra WHERE com_id = %s", (COM_ID,))
    current_app.mysql.connection.commit()
    c.close()
    return {"mensaje": "Compra eliminada correctamente"}
