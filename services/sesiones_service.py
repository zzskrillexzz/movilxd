from flask import current_app
from models.sesiones_model import sesiones

def listarSesiones():
    c = current_app.mysql.connection.cursor()
    sql = "SELECT ses_id, ses_usu_id_fk, ses_fecha_inicio, ses_fecha_fin, ses_ip, ses_activa FROM t_sesion"
    c.execute(sql)
    datos = c.fetchall()
    lista = []
    for p in datos:
        s = sesiones(p[0], p[1], p[2], p[3], p[4], p[5]).todic()
        lista.append(s)
    return lista

def registrarSesiones(SES_ID, SES_USU_ID_FK, SES_FECHA_INICIO, SES_FECHA_FIN, SES_IP, SES_ACTIVA):
    c = current_app.mysql.connection.cursor()
    sql = """
        INSERT INTO t_sesion (ses_id, ses_usu_id_fk, ses_fecha_inicio, ses_fecha_fin, ses_ip, ses_activa) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    c.execute(sql, (SES_ID, SES_USU_ID_FK, SES_FECHA_INICIO, SES_FECHA_FIN, SES_IP, SES_ACTIVA))
    current_app.mysql.connection.commit()
    id = c.lastrowid
    c.close()
    return sesiones(SES_ID, SES_USU_ID_FK, SES_FECHA_INICIO, SES_FECHA_FIN, SES_IP, SES_ACTIVA).todic()

def editarSesiones(SES_ID, SES_USU_ID_FK, SES_FECHA_INICIO, SES_FECHA_FIN, SES_IP, SES_ACTIVA):
    c = current_app.mysql.connection.cursor()
    sql = """
        UPDATE t_sesion 
        SET ses_usu_id_fk=%s, ses_fecha_inicio=%s, ses_fecha_fin=%s, ses_ip=%s, ses_activa=%s
        WHERE ses_id=%s
    """
    c.execute(sql, (SES_USU_ID_FK, SES_FECHA_INICIO, SES_FECHA_FIN, SES_IP, SES_ACTIVA, SES_ID))
    current_app.mysql.connection.commit()
    c.close()
    return sesiones(SES_ID, SES_USU_ID_FK, SES_FECHA_INICIO, SES_FECHA_FIN, SES_IP, SES_ACTIVA).todic()


def eliminarSesiones(SES_ID):
    c = current_app.mysql.connection.cursor()
    sql = "DELETE FROM t_sesion WHERE ses_id = %s"
    c.execute(sql, (SES_ID,))
    current_app.mysql.connection.commit()
    c.close()
    return {"mensaje": "Sesión eliminada", "ses_id": SES_ID}


def buscarSesiones(SES_ID):
    c = current_app.mysql.connection.cursor()
    sql = """
        SELECT ses_id, ses_usu_id_fk, ses_fecha_inicio, ses_fecha_fin, ses_ip, ses_activa 
        FROM t_sesion 
        WHERE ses_id = %s
    """
    c.execute(sql, (SES_ID,))
    p = c.fetchone()
    c.close()
    
    if p:
        return sesiones(p[0], p[1], p[2], p[3], p[4], p[5]).todic()
    return None