class proveedores:
    def __init__(self, provID, provNit=None, provNombre=None, provTipo=None, provContacto=None, provDireccion=None, provEmail=None):
        self.prov_id = provID
        self.prov_nit = provNit
        self.prov_nombre = provNombre
        self.prov_tipo = provTipo
        self.prov_contacto = provContacto
        self.prov_direccion = provDireccion
        self.prov_email = provEmail

    def todic(self):
        return {
            "prov_id": self.prov_id,
            "prov_nit": self.prov_nit,
            "prov_nombre": self.prov_nombre,
            "prov_tipo": self.prov_tipo,
            "prov_contacto": self.prov_contacto,
            "prov_telefono": self.prov_contacto,
            "prov_direccion": self.prov_direccion,
            "prov_email": self.prov_email,
            "prov_correo": self.prov_email
        }
