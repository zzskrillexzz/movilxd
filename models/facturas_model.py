class facturas:
    def __init__(self, id=None, fecha_emision=None, email_enviado=None, 
                 forma_pago=None, cuenta_bancaria=None, total=None, usuario_id=None, fac_estado='Vigente'):
        self.id = id
        self.fecha_emision = fecha_emision
        self.email_enviado = email_enviado
        self.forma_pago = forma_pago
        self.cuenta_bancaria = cuenta_bancaria
        self.total = total
        self.usuario_id = usuario_id
        self.fac_estado = fac_estado

    def todic(self):
        return {
            "id": self.id,
            "fecha_emision": self.fecha_emision,
            "email_enviado": self.email_enviado,
            "forma_pago": self.forma_pago,
            "cuenta_bancaria": self.cuenta_bancaria,
            "total": self.total,
            "usuario_id": self.usuario_id,
            "estado": self.fac_estado
        }