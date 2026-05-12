class lotes:
    def __init__(self, lot_id, lot_numero, lot_fecha_fabricacion, lot_fecha_vencimiento, 
                 lot_cantidad_inicial, lot_cantidad_actual, lot_pro_id_fk, lot_prov_id_fk, lot_estado):
        self.lot_id = lot_id
        self.lot_numero = lot_numero
        self.lot_fecha_fabricacion = lot_fecha_fabricacion
        self.lot_fecha_vencimiento = lot_fecha_vencimiento
        self.lot_cantidad_inicial = lot_cantidad_inicial
        self.lot_cantidad_actual = lot_cantidad_actual
        self.lot_pro_id_fk = lot_pro_id_fk
        self.lot_prov_id_fk = lot_prov_id_fk
        self.lot_estado = lot_estado
    
    def todic(self):
        return {
            "lot_id": self.lot_id,
            "lot_numero": self.lot_numero,
            "lot_fecha_fabricacion": str(self.lot_fecha_fabricacion) if self.lot_fecha_fabricacion else None,
            "lot_fecha_vencimiento": str(self.lot_fecha_vencimiento) if self.lot_fecha_vencimiento else None,
            "lot_cantidad_inicial": self.lot_cantidad_inicial,
            "lot_cantidad_actual": self.lot_cantidad_actual,
            "lot_pro_id_fk": self.lot_pro_id_fk,
            "lot_prov_id_fk": self.lot_prov_id_fk,
            "lot_estado": self.lot_estado
        }