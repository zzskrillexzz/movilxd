class roles:
    def __init__(self, rol_id, rol_nombre, rol_descripcion=None, rol_estado=1):
        self.rol_id = rol_id
        self.rol_nombre = rol_nombre
        self.rol_descripcion = rol_descripcion
        self.rol_estado = rol_estado

    def toDic(self):
        return {
            "id": self.rol_id,
            "nombre": self.rol_nombre,
            "descripcion": self.rol_descripcion,
            "estado": self.rol_estado
        }