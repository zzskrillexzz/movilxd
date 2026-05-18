from flask import current_app

def generarIdSiguiente(tabla, columna_id, prefijo, digitos=3):
    """
    Genera el siguiente ID secuencial para una tabla.
    Ej: generarIdSiguiente('t_pedido', 'ped_id', 'PED') -> 'PED006'
    """
    c = current_app.mysql.connection.cursor()
    sql = f"SELECT {columna_id} FROM {tabla} ORDER BY LENGTH({columna_id}) DESC, {columna_id} DESC LIMIT 1"
    c.execute(sql)
    row = c.fetchone()
    c.close()
    if row:
        last_id = row[0]
        # Extraer el numero del ID
        num_str = last_id[len(prefijo):]
        try:
            last_num = int(num_str)
            return f"{prefijo}{last_num + 1:0{digitos}d}"
        except ValueError:
            # Si no se puede parsear, empezar desde 1
            return f"{prefijo}{1:0{digitos}d}"
    return f"{prefijo}{1:0{digitos}d}"
