class monitoria:
    def __init__(self, mon_id, mon_pro_id_fk, mon_lot_id_fk, mon_inm_id_fk, mon_fecha, mon_tipo, 
                 mon_cantidad, mon_saldo_anterior, mon_saldo_actual, mon_costo_unitario, mon_costo_total):
        self.mon_id = mon_id
        self.mon_pro_id_fk = mon_pro_id_fk
        self.mon_lot_id_fk = mon_lot_id_fk
        self.mon_inm_id_fk = mon_inm_id_fk
        self.mon_fecha = mon_fecha
        self.mon_tipo = mon_tipo
        self.mon_cantidad = mon_cantidad
        self.mon_saldo_anterior = mon_saldo_anterior
        self.mon_saldo_actual = mon_saldo_actual
        self.mon_costo_unitario = mon_costo_unitario
        self.mon_costo_total = mon_costo_total
    
    def todic(self):
        return {
            "mon_id": self.mon_id,
            "mon_pro_id_fk": self.mon_pro_id_fk,
            "mon_lot_id_fk": self.mon_lot_id_fk,
            "mon_inm_id_fk": self.mon_inm_id_fk,
            "mon_fecha": str(self.mon_fecha) if self.mon_fecha else None,
            "mon_tipo": self.mon_tipo,
            "mon_cantidad": self.mon_cantidad,
            "mon_saldo_anterior": self.mon_saldo_anterior,
            "mon_saldo_actual": self.mon_saldo_actual,
            "mon_costo_unitario": float(self.mon_costo_unitario) if self.mon_costo_unitario else None,
            "mon_costo_total": float(self.mon_costo_total) if self.mon_costo_total else None
        }

    @staticmethod
    def update_monitoria(mysql, mon_id, cantidad, saldo_actual, costo_total):
        cur = mysql.connection.cursor()
        sql = "UPDATE t_monitoria SET mon_cantidad = %s, mon_saldo_actual = %s, mon_costo_total = %s WHERE mon_id = %s"
        cur.execute(sql, (cantidad, saldo_actual, costo_total, mon_id))
        mysql.connection.commit()
        filas_afectadas = cur.rowcount
        cur.close()
        return filas_afectadas