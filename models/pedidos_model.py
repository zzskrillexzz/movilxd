import base64

class pedidos:
    def __init__(self, ID, FECHA, METODO_DE_PAGO, CUENTA_BANCARIA=None, ped_comprobante=None, ped_comprobante_tipo=None, ESTADO=None, TOTAL=None, ID_CLIENTE=None, ped_det_id_fk=None, ped_usu_id_fk=None):
        self.ped_id = ID
        self.ped_fecha = FECHA
        self.ped_metodo_pago = METODO_DE_PAGO
        self.ped_cuenta_bancaria = CUENTA_BANCARIA
        self.ped_comprobante = ped_comprobante
        self.ped_comprobante_tipo = ped_comprobante_tipo
        self.ped_estado_entrega = ESTADO
        self.ped_total = TOTAL
        self.ped_cli_id_fk = ID_CLIENTE
        self.ped_det_id_fk = ped_det_id_fk
        self.ped_usu_id_fk = ped_usu_id_fk

    def a_diccionario(self):
        result = {
            "ped_id": self.ped_id,
            "ped_fecha": str(self.ped_fecha) if self.ped_fecha else None,
            "ped_metodo_pago": self.ped_metodo_pago,
            "ped_cuenta_bancaria": self.ped_cuenta_bancaria,
            "ped_estado_entrega": self.ped_estado_entrega,
            "ped_total": float(self.ped_total) if self.ped_total else None,
            "ped_cli_id_fk": self.ped_cli_id_fk,
            "ped_det_id_fk": self.ped_det_id_fk,
            "ped_usu_id_fk": self.ped_usu_id_fk,
        }
        if self.ped_comprobante:
            if isinstance(self.ped_comprobante, bytes):
                result["ped_comprobante"] = base64.b64encode(self.ped_comprobante).decode('utf-8')
            else:
                result["ped_comprobante"] = self.ped_comprobante
        else:
            result["ped_comprobante"] = None
        result["ped_comprobante_tipo"] = self.ped_comprobante_tipo
        return result
