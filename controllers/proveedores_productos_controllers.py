from flask import jsonify, request, current_app
from services.proveedores_productos_service import (
    listarProveedoresProductos, 
    registrarProveedoresProductos, 
    eliminarProveedoresProductos,
    buscarProductosPorProveedor,
    buscarProductosPorProveedorConDatos,
    buscarProveedoresPorProducto
)
from utils.error_handler import safe_controller

@safe_controller
def cnlistadoproveedoresproductos():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    q = request.args.get('q', None)
    order_by = request.args.get('order_by', None)
    filtros = {k: v for k, v in request.args.items() if k not in ('page', 'limit', 'q', 'order_by')}
    datos = listarProveedoresProductos(page=page, limit=limit, q=q, order_by=order_by, **filtros)
    return jsonify(datos), 200

@safe_controller
def cnregistrarproveedoresproductos():
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

    requerido = ["ppp_prov_id_fk", "ppp_pro_id_fk"]
    faltantes = [x for x in requerido if x not in data or str(data[x]).strip() == ""]
    if faltantes:
        return jsonify({"mensaje": f"Faltan los siguientes campos o están vacíos: {faltantes}"}), 400

    c = current_app.mysql.connection.cursor()

    # Validar que el proveedor exista
    c.execute("SELECT prov_id FROM t_proveedor WHERE prov_id = %s", (data["ppp_prov_id_fk"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": f"No existe un proveedor con el ID {data['ppp_prov_id_fk']}"}), 404

    # Validar que el producto exista
    c.execute("SELECT pro_id FROM t_producto WHERE pro_id = %s", (data["ppp_pro_id_fk"],))
    if not c.fetchone():
        c.close()
        return jsonify({"mensaje": f"No existe un producto con el ID {data['ppp_pro_id_fk']}"}), 404

    # Validar relación duplicada
    c.execute("SELECT ppp_prov_id_fk FROM t_proveedor_producto WHERE ppp_prov_id_fk = %s AND ppp_pro_id_fk = %s", 
              (data["ppp_prov_id_fk"], data["ppp_pro_id_fk"]))
    if c.fetchone():
        c.close()
        return jsonify({"mensaje": f"Ya existe la relación entre proveedor {data['ppp_prov_id_fk']} y producto {data['ppp_pro_id_fk']}"}), 409
    c.close()

    resultado = registrarProveedoresProductos(data["ppp_prov_id_fk"], data["ppp_pro_id_fk"])
    return jsonify({"mensaje": "Relación proveedor-producto registrada correctamente", "datos": resultado}), 201

def cneliminarproveedoresproductos():
    requerido = ["ppp_prov_id_fk", "ppp_pro_id_fk"]
    faltantes = [x for x in requerido if x not in request.json]
    if faltantes:
        return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

    proveedor_id = request.json["ppp_prov_id_fk"]
    producto_id = request.json["ppp_pro_id_fk"]
    resultado = eliminarProveedoresProductos(proveedor_id, producto_id)
    return jsonify(resultado), 200

@safe_controller
def cnbuscarproductosporproveedor(prov_id):
    datos = buscarProductosPorProveedor(prov_id)
    if datos:
        return jsonify(datos), 200
    return jsonify({"mensaje": "No se encontraron productos para este proveedor"}), 404

@safe_controller
def cnbuscarproductosporproveedorcondatos(prov_id):
    datos = buscarProductosPorProveedorConDatos(prov_id)
    return jsonify(datos), 200

@safe_controller
def cnbuscarproveedoresporproducto(pro_id):
    datos = buscarProveedoresPorProducto(pro_id)
    if datos:
        return jsonify(datos), 200
    return jsonify({"mensaje": "No se encontraron proveedores para este producto"}), 404
