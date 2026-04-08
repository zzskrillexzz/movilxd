class detalle_de_pedido:
    def __init__(self, ID, CATIDAD, SUBTOTAL):
        self.det_id = ID
        self.det_cantidad = CATIDAD
        self.det_subtotal = SUBTOTAL

    def diccionario_ped(self):
        return{
            "ID":self.det_id,
            "CANTIDAD": int(self.det_cantidad),
            "SUB TOTAL": float(self.det_subtotal)
        }