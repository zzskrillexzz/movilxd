class compras:
    def __init__(self, com_id, com_fecha, com_prov_id_fk, com_usu_id_fk, com_total, com_estado, com_observacion, com_comprobante=None, com_comprobante_tipo=None):
        self.com_id = com_id
        self.com_fecha = com_fecha
        self.com_prov_id_fk = com_prov_id_fk
        self.com_usu_id_fk = com_usu_id_fk
        self.com_total = com_total
        self.com_estado = com_estado
        self.com_observacion = com_observacion
        self.com_comprobante = com_comprobante
        self.com_comprobante_tipo = com_comprobante_tipo
    
    def todic(self):
        import base64
        result = {
            "comp_id": self.com_id,
            "comp_fecha": str(self.com_fecha) if self.com_fecha else None,
            "comp_prov_id_fk": self.com_prov_id_fk,
            "comp_usu_id_fk": self.com_usu_id_fk,
            "comp_total": float(self.com_total) if self.com_total else None,
            "comp_estado": self.com_estado,
            "comp_observacion": self.com_observacion,
        }
        if self.com_comprobante:
            if isinstance(self.com_comprobante, bytes):
                result["comp_comprobante"] = base64.b64encode(self.com_comprobante).decode('utf-8')
            else:
                result["comp_comprobante"] = self.com_comprobante
        else:
            result["comp_comprobante"] = None
        result["comp_comprobante_tipo"] = self.com_comprobante_tipo
        return result
