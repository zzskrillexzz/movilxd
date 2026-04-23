class detalles_pedidos:
        def __init__(self, ID, CANTIDAD, SUBTOTAL, det_ped_id_fk=None, det_pro_id_fk=None, det_precio_unitario=None):
            self.det_id = ID
            self.det_cantidad = CANTIDAD
            self.det_subtotal = SUBTOTAL
            self.det_ped_id_fk = det_ped_id_fk
            self.det_pro_id_fk = det_pro_id_fk
            self.det_precio_unitario = det_precio_unitario

def diccionario_ped(self):
        return {
            "ID": self.det_id,
            "CANTIDAD": int(self.det_cantidad),
            "SUB TOTAL": float(self.det_subtotal),
            "pedido_id": self.det_ped_id_fk,
            "producto_id": self.det_pro_id_fk,
            "precio_unitario": float(self.det_precio_unitario) if self.det_precio_unitario else None
        }
    
    

def diccionario_ped(self):
        return {
            "ID": self.det_id,
            "CANTIDAD": self.det_cantidad,
            "SUB TOTAL": self.det_subtotal,
            "pedido_id": self.det_ped_id_fk,
            "producto_id": self.det_pro_id_fk,
            "precio_unitario": self.det_precio_unitario
        }

@staticmethod
def update_detalle(mysql, det_id, cantidad, subtotal):
        cur = mysql.connection.cursor()
        sql = "UPDATE t_detalle_pedido SET det_cantidad = %s, det_subtotal = %s WHERE det_id = %s"
        cur.execute(sql, (cantidad, subtotal, det_id))
        mysql.connection.commit()
        cur.close()
        return cur.rowcount