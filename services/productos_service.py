from flask import current_app
from models.productos_model import productos

def listarProductos():
    c = current_app.mysql.connection.cursor()
    sql = "SELECT pro_id, pro_nombre, pro_categoria, pro_descripcion, pro_precio, pro_cantidad_disponible, pro_stock_minimo, pro_fecha_caducidad, pro_estado, pro_prov_id_fk FROM t_producto"
    c.execute(sql)
    reg = c.fetchall()
    lista = []
    for p in reg:
        prod = productos(
            proID=p[0], proNombre=p[1], proCategoria=p[2], proDescripcion=p[3],
            proPrecio=p[4], proCantidad=p[5], proStockMinimo=p[6],
            proFechaCaducidad=p[7], proEstado=p[8], proIDprovedor=p[9]
        ).toDic()
        lista.append(prod)
    return lista

def registrarProductos(data):
    try:
        cursor = current_app.mysql.connection.cursor()
        sql = """
            INSERT INTO t_producto (pro_id, pro_nombre, pro_categoria, pro_descripcion, pro_precio, 
                                    pro_cantidad_disponible, pro_stock_minimo, pro_fecha_caducidad, pro_estado, pro_prov_id_fk)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            data.get('id'),
            data.get('nombre'),
            data.get('categoria'),
            data.get('descripcion'),
            data.get('precio'),
            data.get('cantidad_disponible'),
            data.get('stock_minimo', 10),
            data.get('fecha_caducidad'),
            data.get('estado', 'Activo'),
            data.get('proveedor_id')
        ))
        current_app.mysql.connection.commit()
        cursor.close()
        return {"mensaje": "Producto registrado correctamente"}
    except Exception as e:
        raise e

def editarProductos(pro_id, data):
    try:
        cursor = current_app.mysql.connection.cursor()
        sql = """
            UPDATE t_producto
            SET pro_nombre=%s, pro_categoria=%s, pro_descripcion=%s, pro_precio=%s,
                pro_cantidad_disponible=%s, pro_stock_minimo=%s, pro_fecha_caducidad=%s,
                pro_estado=%s, pro_prov_id_fk=%s
            WHERE pro_id=%s
        """
        cursor.execute(sql, (
            data.get('nombre'),
            data.get('categoria'),
            data.get('descripcion'),
            data.get('precio'),
            data.get('cantidad_disponible'),
            data.get('stock_minimo', 10),
            data.get('fecha_caducidad'),
            data.get('estado', 'Activo'),
            data.get('proveedor_id'),
            pro_id
        ))
        current_app.mysql.connection.commit()
        cursor.close()
        return {"mensaje": "Producto actualizado correctamente"}
    except Exception as e:
        raise e
