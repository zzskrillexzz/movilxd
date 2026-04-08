from flask import current_app
from models.pedido_model import pedido

def listarPedido():
    c = current_app.mysql.connection.cursor()
    
    sql = "SELECT ped_id, ped_fecha, ped_metodo_pago, ped_estado_entrega, ped_total, ped_cli_id_fk, ped_det_id_fk From t_pedido"
    c.execute(sql)
    reg = c.fetchall()
    
    listav = []
    
    for p in reg:
        ped = pedido(
            ID = int(p[0]) if str(p[0]).isdigit() else None,
            FECHA             = p[1],
            METODO_DE_PAGO    = p[2],
            ESTADO            = p[3],
            TOTAL             = p[4],
            ID_CLIENTE        = p[5],
            DETALLES          = p[6]
        ).a_diccionario()
        listav.append(ped)
        
    return listav


def registrarpedido(ID, FECHA, METODO_DE_PAGO, ESTADO, TOTAL, ID_CLIENTE, DETALLES):
    c = current_app.mysql.connection.cursor()
    sql = "insert into t_pedido (ped_id, ped_fecha, ped_metodo_pago, ped_estado_entrega, ped_total, ped_cli_id_fk, ped_det_id_fk) values (%s,%s,%s,%s,%s,%s,%s)"
    
    c.execute(sql,(ID, FECHA, METODO_DE_PAGO, ESTADO, TOTAL, ID_CLIENTE, DETALLES))
    current_app.mysql.connection.commit()
    
    id = c.lastrowid
    c.close()
    return pedido(ID, FECHA, METODO_DE_PAGO, ESTADO, TOTAL, ID_CLIENTE, DETALLES).a_diccionario

    return