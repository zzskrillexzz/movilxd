from flask import current_app
from models.proveedores_productos_model import proveedores_productos
from utils.search_builder import SearchBuilder

def listarProveedoresProductos(page=1, limit=50, q=None, order_by=None, **filters):
    c = current_app.mysql.connection.cursor()
    sb = SearchBuilder(
        table='t_proveedor_producto',
        search_fields=['ppp_prov_id_fk', 'ppp_pro_id_fk'],
        exact_fields=['ppp_prov_id_fk', 'ppp_pro_id_fk'],
        default_order='ppp_prov_id_fk ASC'
    )
    result = sb.execute(c, page=page, limit=limit, q=q, order_by=order_by, **filters)
    c.close()

    lista = []
    for item in result['data']:
        pp = proveedores_productos(
            ppp_prov_id_fk=item['ppp_prov_id_fk'],
            ppp_pro_id_fk=item['ppp_pro_id_fk']
        ).todic()
        lista.append(pp)

    result['data'] = lista
    return result


def registrarProveedoresProductos(PPP_PROV_ID_FK, PPP_PRO_ID_FK):
    c = current_app.mysql.connection.cursor()
    sql = """
        INSERT INTO t_proveedor_producto (ppp_prov_id_fk, ppp_pro_id_fk) 
        VALUES (%s, %s)
    """
    c.execute(sql, (PPP_PROV_ID_FK, PPP_PRO_ID_FK))
    current_app.mysql.connection.commit()
    id = c.lastrowid
    c.close()
    return proveedores_productos(PPP_PROV_ID_FK, PPP_PRO_ID_FK).todic()


def eliminarProveedoresProductos(PPP_PROV_ID_FK, PPP_PRO_ID_FK):
    c = current_app.mysql.connection.cursor()
    sql = """
        DELETE FROM t_proveedor_producto 
        WHERE ppp_prov_id_fk = %s AND ppp_pro_id_fk = %s
    """
    c.execute(sql, (PPP_PROV_ID_FK, PPP_PRO_ID_FK))
    current_app.mysql.connection.commit()
    c.close()
    return {"mensaje": "Relación proveedor-producto eliminada correctamente"}


def buscarProductosPorProveedor(PPP_PROV_ID_FK):
    c = current_app.mysql.connection.cursor()
    sql = "SELECT ppp_prov_id_fk, ppp_pro_id_fk FROM t_proveedor_producto WHERE ppp_prov_id_fk = %s"
    c.execute(sql, (PPP_PROV_ID_FK,))
    datos = c.fetchall()
    
    lista = []
    for p in datos:
        pp = proveedores_productos(p[0], p[1]).todic()
        lista.append(pp)
    
    return lista


def buscarProductosPorProveedorConDatos(PPP_PROV_ID_FK, q=None, page=1, limit=8):
    """
    Retorna productos de un proveedor con todos los datos del producto (JOIN)
    con soporte de búsqueda (q) y paginación.
    """
    c = current_app.mysql.connection.cursor()

    base_where = "WHERE pp.ppp_prov_id_fk = %s"
    params = [PPP_PROV_ID_FK]

    if q and q.strip():
        like = f'%{q.strip()}%'
        base_where += " AND (p.pro_id LIKE %s OR p.pro_nombre LIKE %s OR p.pro_categoria LIKE %s)"
        params.extend([like, like, like])

    c.execute(f"SELECT COUNT(*) FROM t_proveedor_producto pp JOIN t_producto p ON p.pro_id = pp.ppp_pro_id_fk {base_where}", params)
    total = c.fetchone()[0]

    offset = (page - 1) * limit
    c.execute(f"""
        SELECT p.pro_id, p.pro_nombre, p.pro_categoria, p.pro_descripcion,
               p.pro_precio, p.pro_estado
        FROM t_proveedor_producto pp
        JOIN t_producto p ON p.pro_id = pp.ppp_pro_id_fk
        {base_where}
        ORDER BY p.pro_nombre ASC
        LIMIT %s OFFSET %s
    """, params + [limit, offset])
    rows = c.fetchall()
    c.close()

    from models.productos_model import productos
    lista = [productos(r[0], r[1], r[2], r[3], r[4], r[5]).toDic() for r in rows]

    pages = max(1, -(-total // limit))
    return {'data': lista, 'total': total, 'page': page, 'limit': limit, 'pages': pages}


def buscarProveedoresPorProducto(PPP_PRO_ID_FK):
    c = current_app.mysql.connection.cursor()
    sql = "SELECT ppp_prov_id_fk, ppp_pro_id_fk FROM t_proveedor_producto WHERE ppp_pro_id_fk = %s"
    c.execute(sql, (PPP_PRO_ID_FK,))
    datos = c.fetchall()
    
    lista = []
    for p in datos:
        pp = proveedores_productos(p[0], p[1]).todic()
        lista.append(pp)
    
    return lista
