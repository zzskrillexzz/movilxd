class kardex:
    def __init__(self, kar_id, kar_pro_id_fk, kar_lot_id_fk, kar_inm_id_fk, kar_fecha, kar_tipo, kar_cantidad, kar_saldo_anterior, kar_saldo_actual, kar_costo_unitario, kar_costo_total):
        self.kar_id = kar_id
        self.kar_pro_id_fk = kar_pro_id_fk
        self.kar_lot_id_fk = kar_lot_id_fk
        self.kar_inm_id_fk = kar_inm_id_fk
        self.kar_fecha = kar_fecha
        self.kar_tipo = kar_tipo
        self.kar_cantidad = kar_cantidad
        self.kar_saldo_anterior = kar_saldo_anterior
        self.kar_saldo_actual = kar_saldo_actual
        self.kar_costo_unitario = kar_costo_unitario
        self.kar_costo_total = kar_costo_total
    
    def todic(self):
        return {
            "id": self.kar_id,
            "producto_id": self.kar_pro_id_fk,
            "lote_id": self.kar_lot_id_fk,
            "movimiento_id": self.kar_inm_id_fk,
            "fecha": self.kar_fecha,
            "tipo": self.kar_tipo,
            "cantidad": self.kar_cantidad,
            "saldo_anterior": self.kar_saldo_anterior,
            "saldo_actual": self.kar_saldo_actual,
            "costo_unitario": self.kar_costo_unitario,
            "costo_total": self.kar_costo_total
        }

    @staticmethod
    def update_kardex(mysql, kar_id, cantidad, saldo_actual, costo_total):
        cur = mysql.connection.cursor()
        sql = "UPDATE t_kardex SET kar_cantidad = %s, kar_saldo_actual = %s, kar_costo_total = %s WHERE kar_id = %s"
        cur.execute(sql, (cantidad, saldo_actual, costo_total, kar_id))
        mysql.connection.commit()
        cur.close()
        return cur.rowcount