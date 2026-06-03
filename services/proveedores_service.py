from flask import current_app
from models.proveedores_model import proveedores
from utils.search_builder import SearchBuilder

def listarProveedores(page=1, limit=50, q=None, order_by=None, **filters):
    c = current_app.mysql.connection.cursor()
    sb = SearchBuilder(
        table='t_proveedor',
        search_fields=['prov_id', 'prov_nit', 'prov_nombre', 'prov_tipo', 'prov_contacto', 'prov_email'],
        exact_fields=['prov_tipo'],
        default_order='prov_id ASC'
    )
    result = sb.execute(c, page=page, limit=limit, q=q, order_by=order_by, **filters)
    c.close()

    lista = []
    for item in result['data']:
        prov = proveedores(
            provID=item['prov_id'], provNit=item['prov_nit'], provNombre=item['prov_nombre'],
            provTipo=item['prov_tipo'], provContacto=item['prov_contacto'],
            provDireccion=item['prov_direccion'], provEmail=item['prov_email']
        ).todic()
        lista.append(prov)

    result['data'] = lista
    return result

def registrarProveedores(data):
    try:
        cursor = current_app.mysql.connection.cursor()
        sql = """
            INSERT INTO t_proveedor (prov_id, prov_nit, prov_nombre, prov_tipo, prov_contacto, prov_direccion, prov_email)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            data.get('id'),
            data.get('nit'),
            data.get('nombre'),
            data.get('tipo', 'Laboratorio'),
            data.get('contacto'),
            data.get('direccion'),
            data.get('email')
        ))
        current_app.mysql.connection.commit()
        cursor.close()
        return {"mensaje": "Proveedor registrado correctamente"}
    except Exception as e:
        raise e
