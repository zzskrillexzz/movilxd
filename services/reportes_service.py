from flask import current_app
from models.reportes_model import reportes

def listarReportes():
    c = current_app.mysql.connection.cursor()
    sql = "SELECT rep_id, rep_tipo, rep_fecha, rep_parametros, rep_usu_id_fk, rep_resultado FROM t_reporte"
    c.execute(sql)
    datos = c.fetchall()
    lista = []
    for p in datos:
        r = reportes(p[0], p[1], p[2], p[3], p[4], p[5]).todic()
        lista.append(r)
    return lista

def registrarReportes(REP_ID, REP_TIPO, REP_FECHA, REP_PARAMETROS, REP_USU_ID_FK, REP_RESULTADO):
    c = current_app.mysql.connection.cursor()
    sql = """
        INSERT INTO t_reporte (rep_id, rep_tipo, rep_fecha, rep_parametros, rep_usu_id_fk, rep_resultado) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    c.execute(sql, (REP_ID, REP_TIPO, REP_FECHA, REP_PARAMETROS, REP_USU_ID_FK, REP_RESULTADO))
    current_app.mysql.connection.commit()
    id = c.lastrowid
    c.close()
    return reportes(REP_ID, REP_TIPO, REP_FECHA, REP_PARAMETROS, REP_USU_ID_FK, REP_RESULTADO).todic()



def eliminarReportes(REP_ID):
    c = current_app.mysql.connection.cursor()
    sql = "DELETE FROM t_reporte WHERE rep_id = %s"
    c.execute(sql, (REP_ID,))
    current_app.mysql.connection.commit()
    c.close()
    return {"mensaje": "Reporte eliminado", "rep_id": REP_ID}

def buscarReportes(REP_ID): # <-- IMPORTANTE: Debe tener REP_ID
    c = current_app.mysql.connection.cursor()
    sql = """
        SELECT rep_id, rep_tipo, rep_fecha, rep_parametros, rep_usu_id_fk, rep_resultado 
        FROM t_reporte 
        WHERE rep_id = %s
    """
    c.execute(sql, (REP_ID,))
    p = c.fetchone()
    c.close()
    
    if p:
        return reportes(p[0], p[1], p[2], p[3], p[4], p[5]).todic()
    return None

def editarReportes(REP_ID, REP_TIPO, REP_FECHA, REP_PARAMETROS, REP_USU_ID_FK, REP_RESULTADO):
    c = current_app.mysql.connection.cursor()
    sql = """
        UPDATE t_reporte 
        SET rep_tipo=%s, rep_fecha=%s, rep_parametros=%s, rep_usu_id_fk=%s, rep_resultado=%s
        WHERE rep_id=%s
    """
    c.execute(sql, (REP_TIPO, REP_FECHA, REP_PARAMETROS, REP_USU_ID_FK, REP_RESULTADO, REP_ID))
    current_app.mysql.connection.commit()
    c.close()
    return reportes(REP_ID, REP_TIPO, REP_FECHA, REP_PARAMETROS, REP_USU_ID_FK, REP_RESULTADO).todic()
