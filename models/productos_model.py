class productos:
    def __init__(self, proID, proNombre, proCategoria, proDescripcion, proPrecio, proCantidad,
                 proStockMinimo=10, proFechaCaducidad=None, proEstado='Activo', proIDprovedor=None,
                 proRegistroInvima=None, proFechaVencimientoRegistro=None,
                 proControlEspecial=0, proTipoControl=None):
        self.pro_id = proID
        self.pro_nombre = proNombre
        self.pro_categoria = proCategoria
        self.pro_descripcion = proDescripcion
        self.pro_precio = proPrecio
        self.pro_cantidad_disponible = proCantidad
        self.pro_stock_minimo = proStockMinimo
        self.pro_fecha_caducidad = proFechaCaducidad
        self.pro_registro_invima = proRegistroInvima
        self.pro_fecha_vencimiento_registro = proFechaVencimientoRegistro
        self.pro_control_especial = proControlEspecial
        self.pro_tipo_control = proTipoControl
        self.pro_estado = proEstado
        self.pro_prov_id_fk = proIDprovedor

    def toDic(self):
        return {
            "id": self.pro_id,
            "nombre": self.pro_nombre,
            "categoria": self.pro_categoria,
            "descripcion": self.pro_descripcion,
            "precio": float(self.pro_precio) if self.pro_precio else None,
            "cantidad_disponible": self.pro_cantidad_disponible,
            "stock_minimo": self.pro_stock_minimo,
            "fecha_caducidad": str(self.pro_fecha_caducidad) if self.pro_fecha_caducidad else None,
            "registro_invima": self.pro_registro_invima,
            "fecha_vencimiento_registro": str(self.pro_fecha_vencimiento_registro) if self.pro_fecha_vencimiento_registro else None,
            "control_especial": self.pro_control_especial,
            "tipo_control": self.pro_tipo_control,
            "estado": self.pro_estado,
            "proveedor_id": self.pro_prov_id_fk
        }
