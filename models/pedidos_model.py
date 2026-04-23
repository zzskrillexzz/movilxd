from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime

class pedidos:
    def __init__(self, ID, FECHA, METODO_DE_PAGO, ESTADO, TOTAL, ID_CLIENTE, ped_det_id_fk=None, ped_usu_id_fk=None):
        self.ped_id = ID
        self.ped_fecha = FECHA
        self.ped_metodo_pago = METODO_DE_PAGO
        self.ped_estado_entrega = ESTADO
        self.ped_total = TOTAL
        self.ped_cli_id_fk = ID_CLIENTE
        self.ped_det_id_fk = ped_det_id_fk
        self.ped_usu_id_fk = ped_usu_id_fk

    def a_diccionario(self):
        return {
            "id": self.ped_id,
            "fecha": str(self.ped_fecha) if self.ped_fecha else None,
            "metodo_de_pago": self.ped_metodo_pago,
            "estado": self.ped_estado_entrega,
            "total": float(self.ped_total) if self.ped_total else None,
            "cliente_id": self.ped_cli_id_fk,
            "detalle_pedido_id": self.ped_det_id_fk,
            "usuario_id": self.ped_usu_id_fk
        }

    @staticmethod
    def get_all_pedidos(mysql):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM t_pedido")
        rows = cur.fetchall()
        pedidos_list = []
        for row in rows:
            pedido = pedidos(
                ID=row['ped_id'],
                FECHA=row['ped_fecha'],
                METODO_DE_PAGO=row['ped_metodo_pago'],
                ESTADO=row['ped_estado_entrega'],
                TOTAL=row['ped_total'],
                ID_CLIENTE=row['ped_cli_id_fk'],
                ped_det_id_fk=row.get('ped_det_id_fk'),
                ped_usu_id_fk=row.get('ped_usu_id_fk')
            )
            pedidos_list.append(pedido.a_diccionario())
        cur.close()
        return pedidos_list

    @staticmethod
    def get_pedido_by_id(mysql, ped_id):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM t_pedido WHERE ped_id = %s", (ped_id,))
        row = cur.fetchone()
        cur.close()
        if row:
            pedido = pedidos(
                ID=row['ped_id'],
                FECHA=row['ped_fecha'],
                METODO_DE_PAGO=row['ped_metodo_pago'],
                ESTADO=row['ped_estado_entrega'],
                TOTAL=row['ped_total'],
                ID_CLIENTE=row['ped_cli_id_fk'],
                ped_det_id_fk=row.get('ped_det_id_fk'),
                ped_usu_id_fk=row.get('ped_usu_id_fk')
            )
            return pedido.a_diccionario()
        return None

    @staticmethod
    def create_pedido(mysql, data):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = """INSERT INTO t_pedido 
                    (ped_id, ped_fecha, ped_metodo_pago, ped_estado_entrega, 
                     ped_total, ped_cli_id_fk, ped_det_id_fk, ped_usu_id_fk) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        cur.execute(sql, (
            data.get('ped_id'),
            data.get('ped_fecha'),
            data.get('ped_metodo_pago'),
            data.get('ped_estado_entrega'),
            data.get('ped_total'),
            data.get('ped_cli_id_fk'),
            data.get('ped_det_id_fk'),
            data.get('ped_usu_id_fk')
        ))
        mysql.connection.commit()
        affected = cur.rowcount
        cur.close()
        return affected

    @staticmethod
    def update_pedido(mysql, ped_id, data):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = """UPDATE t_pedido SET 
                    ped_fecha = %s, 
                    ped_metodo_pago = %s, 
                    ped_estado_entrega = %s, 
                    ped_total = %s,
                    ped_cli_id_fk = %s,
                    ped_det_id_fk = %s,
                    ped_usu_id_fk = %s
                 WHERE ped_id = %s"""
        cur.execute(sql, (
            data.get('ped_fecha'),
            data.get('ped_metodo_pago'),
            data.get('ped_estado_entrega'),
            data.get('ped_total'),
            data.get('ped_cli_id_fk'),
            data.get('ped_det_id_fk'),
            data.get('ped_usu_id_fk'),
            ped_id
        ))
        mysql.connection.commit()
        affected = cur.rowcount
        cur.close()
        return affected

    @staticmethod
    def delete_pedido(mysql, ped_id):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("DELETE FROM t_pedido WHERE ped_id = %s", (ped_id,))
        mysql.connection.commit()
        affected = cur.rowcount
        cur.close()
        return affected