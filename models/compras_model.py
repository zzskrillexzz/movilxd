class compras:
    def __init__(self, com_id, com_fecha, com_prov_id_fk, com_usu_id_fk, com_total, com_estado, com_observacion, com_pro_id_fk=None, com_cantidad=None):
        self.com_id = com_id
        self.com_fecha = com_fecha
        self.com_prov_id_fk = com_prov_id_fk
        self.com_usu_id_fk = com_usu_id_fk
        self.com_total = com_total
        self.com_estado = com_estado
        self.com_observacion = com_observacion
        self.com_pro_id_fk = com_pro_id_fk
        self.com_cantidad = com_cantidad
    
    def todic(self):
        return {
            "comp_id": self.com_id,
            "comp_fecha": str(self.com_fecha) if self.com_fecha else None,
            "comp_prov_id_fk": self.com_prov_id_fk,
            "comp_usu_id_fk": self.com_usu_id_fk,
            "comp_total": float(self.com_total) if self.com_total else None,
            "comp_estado": self.com_estado,
            "comp_observacion": self.com_observacion,
            "comp_pro_id_fk": self.com_pro_id_fk,
            "comp_cantidad": self.com_cantidad
        }