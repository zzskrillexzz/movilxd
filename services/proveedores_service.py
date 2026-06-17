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


def buscarProveedores(prov_id):
    """Busca un proveedor por su ID y retorna dict o None."""
    cursor = current_app.mysql.connection.cursor()
    cursor.execute("SELECT * FROM t_proveedor WHERE prov_id = %s", (prov_id,))
    row = cursor.fetchone()
    cursor.close()
    if row:
        return proveedores(
            provID=row['prov_id'], provNit=row['prov_nit'], provNombre=row['prov_nombre'],
            provTipo=row['prov_tipo'], provContacto=row['prov_contacto'],
            provDireccion=row['prov_direccion'], provEmail=row['prov_email']
        ).todic()
    return None


def editarProveedores(prov_id, data):
    """Actualiza un proveedor existente."""
    cursor = current_app.mysql.connection.cursor()
    sql = """
        UPDATE t_proveedor SET
            prov_nit = %s, prov_nombre = %s, prov_tipo = %s,
            prov_contacto = %s, prov_direccion = %s, prov_email = %s
        WHERE prov_id = %s
    """
    cursor.execute(sql, (
        data.get('nit'), data.get('nombre'), data.get('tipo'),
        data.get('contacto'), data.get('direccion'), data.get('email'),
        prov_id
    ))
    current_app.mysql.connection.commit()
    cursor.close()
    return {"mensaje": "Proveedor actualizado correctamente"}


def eliminarProveedores(prov_id):
    """Elimina un proveedor por su ID."""
    cursor = current_app.mysql.connection.cursor()
    cursor.execute("DELETE FROM t_proveedor WHERE prov_id = %s", (prov_id,))
    current_app.mysql.connection.commit()
    cursor.close()
    return {"mensaje": "Proveedor eliminado correctamente"}
