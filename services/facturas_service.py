from flask import current_app
from models.facturas_model import facturas
from utils.search_builder import SearchBuilder

def listarFacturas(page=1, limit=50, q=None, order_by=None, **filters):
    c = current_app.mysql.connection.cursor()
    sb = SearchBuilder(
        table='t_factura f',
        search_fields=['fac_id', 'fac_forma_pago', 'fac_estado'],
        exact_fields=['fac_estado', 'fac_forma_pago', 'fac_usu_id_fk', 'fac_cli_id_fk'],
        range_fields={'fac_fecha_emision': 'date', 'fac_total': 'decimal'},
        join_clause='LEFT JOIN t_pedido ON fac_id = ped_id LEFT JOIN t_cliente ON ped_cli_id_fk = cli_id',
        select_columns='f.*, cli_nombre, cli_apellido, cli_correo, ped_cli_id_fk as fac_cli_id_fk',
        default_order='fac_id ASC'
    )
    result = sb.execute(c, page=page, limit=limit, q=q, order_by=order_by, **filters)
    c.close()

    lista = []
    for item in result['data']:
        fac = facturas(
            id=item['fac_id'], fecha_emision=item['fac_fecha_emision'],
            email_enviado=item['fac_email_enviado'],
            forma_pago=item['fac_forma_pago'], cuenta_bancaria=item['fac_cuenta_bancaria'],
            total=item['fac_total'], usuario_id=item['fac_usu_id_fk'],
            fac_estado=item['fac_estado'],
            cli_id_fk=item.get('fac_cli_id_fk'),
            cli_nombre=item.get('cli_nombre'),
            cli_apellido=item.get('cli_apellido'),
            cli_correo=item.get('cli_correo')
        ).todic()
        lista.append(fac)

    result['data'] = lista
    return result

def registrarFacturas(data):
    try:
        cursor = current_app.mysql.connection.cursor()

        # Intentar con fac_cli_id_fk; si la columna no existe, insertar sin ella
        try:
            sql = """
                INSERT INTO t_factura (fac_id, fac_fecha_emision, fac_email_enviado, fac_forma_pago, fac_cuenta_bancaria, fac_total, fac_usu_id_fk, fac_estado, fac_cli_id_fk)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data.get('id'),
                data.get('fecha_emision'),
                data.get('email_enviado', 0),
                data.get('forma_pago'),
                data.get('cuenta_bancaria') or data.get('fac_cuenta_bancaria'),
                data.get('total'),
                data.get('usuario_id'),
                data.get('estado', 'Vigente'),
                data.get('cli_id_fk')
            ))
        except Exception:
            # Columna fac_cli_id_fk no existe aún — insertar sin ella
            sql = """
                INSERT INTO t_factura (fac_id, fac_fecha_emision, fac_email_enviado, fac_forma_pago, fac_cuenta_bancaria, fac_total, fac_usu_id_fk, fac_estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data.get('id'),
                data.get('fecha_emision'),
                data.get('email_enviado', 0),
                data.get('forma_pago'),
                data.get('cuenta_bancaria') or data.get('fac_cuenta_bancaria'),
                data.get('total'),
                data.get('usuario_id'),
                data.get('estado', 'Vigente')
            ))

        current_app.mysql.connection.commit()
        cursor.close()
        return {"mensaje": "Factura registrada correctamente"}
    except Exception as e:
        raise e

def editarFacturas(fac_id, data):
    try:
        cursor = current_app.mysql.connection.cursor()

        # Intentar con fac_cli_id_fk; si la columna no existe, actualizar sin ella
        try:
            sql = """
                UPDATE t_factura SET fac_fecha_emision=%s, fac_email_enviado=%s, fac_forma_pago=%s,
                fac_cuenta_bancaria=%s, fac_total=%s, fac_usu_id_fk=%s, fac_estado=%s, fac_cli_id_fk=%s WHERE fac_id=%s
            """
            cursor.execute(sql, (
                data.get('fecha_emision'), data.get('email_enviado'), data.get('forma_pago'),
                data.get('cuenta_bancaria') or data.get('fac_cuenta_bancaria'),
                data.get('total'), data.get('usuario_id'), data.get('estado'),
                data.get('cli_id_fk'), fac_id
            ))
        except Exception:
            # Columna fac_cli_id_fk no existe aún — actualizar sin ella
            sql = """
                UPDATE t_factura SET fac_fecha_emision=%s, fac_email_enviado=%s, fac_forma_pago=%s,
                fac_cuenta_bancaria=%s, fac_total=%s, fac_usu_id_fk=%s, fac_estado=%s WHERE fac_id=%s
            """
            cursor.execute(sql, (
                data.get('fecha_emision'), data.get('email_enviado'), data.get('forma_pago'),
                data.get('cuenta_bancaria') or data.get('fac_cuenta_bancaria'),
                data.get('total'), data.get('usuario_id'), data.get('estado'),
                fac_id
            ))

        current_app.mysql.connection.commit()
        cursor.close()
        return {"mensaje": "Factura actualizada correctamente"}
    except Exception as e:
        raise e

def eliminarFacturas(fac_id):
    try:
        cursor = current_app.mysql.connection.cursor()
        sql = "DELETE FROM t_factura WHERE fac_id = %s"
        cursor.execute(sql, (fac_id,))
        current_app.mysql.connection.commit()
        cursor.close()
        return {"mensaje": "Factura eliminada correctamente"}
    except Exception as e:
        raise e

def buscarFacturas(fac_id):
    try:
        cursor = current_app.mysql.connection.cursor()
        sql = """
            SELECT f.fac_id, f.fac_fecha_emision, f.fac_email_enviado, f.fac_forma_pago,
                   f.fac_cuenta_bancaria, f.fac_total, f.fac_usu_id_fk, f.fac_estado,
                   p.ped_cli_id_fk, cl.cli_nombre, cl.cli_apellido, cl.cli_correo
            FROM t_factura f
            LEFT JOIN t_pedido p ON f.fac_id = p.ped_id
            LEFT JOIN t_cliente cl ON p.ped_cli_id_fk = cl.cli_id
            WHERE f.fac_id = %s
        """
        cursor.execute(sql, (fac_id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return facturas(id=row[0], fecha_emision=row[1], email_enviado=row[2],
                          forma_pago=row[3], cuenta_bancaria=row[4], total=row[5],
                          usuario_id=row[6], fac_estado=row[7],
                          cli_id_fk=row[8], cli_nombre=row[9], cli_apellido=row[10], cli_correo=row[11]).todic()
        return None
    except Exception as e:
        raise e
