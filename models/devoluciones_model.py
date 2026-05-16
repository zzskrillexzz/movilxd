class devoluciones:
    def __init__(self, dev_id, dev_ped_id_fk=None, dev_pro_id_fk=None, dev_lot_id_fk=None,
                 dev_cantidad=None, dev_motivo=None, dev_fecha=None, dev_usu_id_fk=None):
        self.dev_id = dev_id
        self.dev_ped_id_fk = dev_ped_id_fk
        self.dev_pro_id_fk = dev_pro_id_fk
        self.dev_lot_id_fk = dev_lot_id_fk
        self.dev_cantidad = dev_cantidad
        self.dev_motivo = dev_motivo
        self.dev_fecha = dev_fecha
        self.dev_usu_id_fk = dev_usu_id_fk

    def todic(self):
        return {
            "id": self.dev_id,
            "pedido_id": self.dev_ped_id_fk,
            "producto_id": self.dev_pro_id_fk,
            "lote_id": self.dev_lot_id_fk,
            "cantidad": self.dev_cantidad,
            "motivo": self.dev_motivo,
            "fecha": str(self.dev_fecha) if self.dev_fecha else None,
            "usuario_id": self.dev_usu_id_fk
        }
