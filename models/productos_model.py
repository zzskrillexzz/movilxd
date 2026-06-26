class productos:
    def __init__(self, proID, proNombre, proCategoria, proDescripcion, proPrecio, proEstado='Activo'):
        self.pro_id = proID
        self.pro_nombre = proNombre
        self.pro_categoria = proCategoria
        self.pro_descripcion = proDescripcion
        self.pro_precio = proPrecio
        self.pro_estado = proEstado

    def toDic(self):
        return {
            "id": self.pro_id,
            "nombre": self.pro_nombre,
            "categoria": self.pro_categoria,
            "descripcion": self.pro_descripcion,
            "precio": float(self.pro_precio) if self.pro_precio else None,
            "estado": self.pro_estado
        }
