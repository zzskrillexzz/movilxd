from flask import current_app
from models.devoluciones_model import devoluciones

def listarDevoluciones():
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT dev_id, dev_ped_id_fk, dev_pro_id_fk, dev_lot_id_fk, dev_cantidad, dev_motivo, dev_fecha, dev_usu_id_fk FROM t_devolucion ORDER BY dev_fecha DESC")
    datos = c.fetchall()
    lista = []
    for p in datos:
        d = devoluciones(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7])
        lista.append(d.todic())
    return lista

def generarId():
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT dev_id FROM t_devolucion ORDER BY dev_id DESC LIMIT 1")
    row = c.fetchone()
    c.close()
    if row:
        last_num = int(row[0].replace('DEV', ''))
        return f"DEV{last_num + 1:03d}"
    return "DEV001"

def registrarDevolucion(dev_ped_id_fk, dev_pro_id_fk, dev_lot_id_fk, dev_cantidad, dev_motivo, dev_fecha, dev_usu_id_fk):
    dev_id = generarId()
    c = current_app.mysql.connection.cursor()
    c.execute("""INSERT INTO t_devolucion (dev_id, dev_ped_id_fk, dev_pro_id_fk, dev_lot_id_fk, dev_cantidad, dev_motivo, dev_fecha, dev_usu_id_fk)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
              (dev_id, dev_ped_id_fk, dev_pro_id_fk, dev_lot_id_fk, dev_cantidad, dev_motivo, dev_fecha, dev_usu_id_fk))
    current_app.mysql.connection.commit()
    c.close()
    return {"mensaje": "Devolucion registrada", "id": dev_id}
