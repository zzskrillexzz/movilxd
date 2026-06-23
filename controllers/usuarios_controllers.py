from flask import jsonify, request, current_app
from services.usuarios_service import listarUsuarios, registrarUsuarios, editarUsuarios, eliminarUsuarios, buscarUsuarios
from utils.validators import validar_campos_texto
from utils.error_handler import safe_controller

@safe_controller
def cnlistadousuarios():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    q = request.args.get('q', None)
    order_by = request.args.get('order_by', None)
    filtros = {k: v for k, v in request.args.items() if k not in ('page', 'limit', 'q', 'order_by')}
    datos = listarUsuarios(page=page, limit=limit, q=q, order_by=order_by, **filtros)
    return jsonify(datos), 200

@safe_controller
def cnregistrarusuarios():
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

    requerido = ["usu_id", "usu_nombre", "usu_rol", "usu_correo", "usu_contrasena", "usu_estado"]
    faltantes = [x for x in requerido if x not in data]
    if faltantes:
        return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

    # Validar campos no vacíos
    for campo in ["usu_id", "usu_nombre", "usu_rol", "usu_correo", "usu_contrasena"]:
        if str(data[campo]).strip() == "":
            return jsonify({"mensaje": f"El campo {campo} no puede estar vacío"}), 400

    # Validar longitud de campos de texto
    errores = validar_campos_texto(data, "usu_nombre", "usu_rol", "usu_correo", "usu_contrasena")
    if errores:
        return jsonify({"mensaje": " | ".join(errores)}), 400

    # Validar rol
    roles_validos = ["Administrador", "Vendedor", "Bodeguero", "Contador"]
    if data["usu_rol"] not in roles_validos:
        return jsonify({"mensaje": f"Rol inválido. Valores permitidos: {roles_validos}"}), 400

    # Validar estado
    if data["usu_estado"] not in [0, 1]:
        return jsonify({"mensaje": "El estado debe ser 0 (Inactivo) o 1 (Activo)"}), 400

    # Validar longitud mínima de contraseña
    if len(str(data["usu_contrasena"]).strip()) < 6:
        return jsonify({"mensaje": "La contraseña debe tener al menos 6 caracteres"}), 400

    # Normalizar correo a minúsculas
    data["usu_correo"] = (data.get("usu_correo") or "").strip().lower()

    # Validar duplicado por ID
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT usu_id FROM t_usuario WHERE usu_id = %s", (data["usu_id"],))
    if c.fetchone():
        c.close()
        return jsonify({"mensaje": f"Ya existe un usuario con el ID {data['usu_id']}"}), 409

    # Validar correo duplicado
    c.execute("SELECT usu_id FROM t_usuario WHERE usu_correo = %s", (data["usu_correo"],))
    if c.fetchone():
        c.close()
        return jsonify({"mensaje": f"Ya existe un usuario con el correo {data['usu_correo']}"}), 409
    c.close()

    ultimo_acceso = data.get("usu_ultimo_acceso")

    resultado = registrarUsuarios(
        data["usu_id"], data["usu_nombre"], data["usu_rol"],
        data["usu_correo"], data["usu_contrasena"], data["usu_estado"], ultimo_acceso
    )
    return jsonify({"mensaje": "Usuario registrado correctamente", "datos": resultado}), 201


@safe_controller
def cneditarusuarios():
    data = request.get_json()
    if not data or "usu_id" not in data:
        return jsonify({"mensaje": "Se requiere el ID del usuario"}), 400

    # Validar campos requeridos para la edición (contraseña es opcional en edición)
    requerido = ["usu_nombre", "usu_rol", "usu_correo", "usu_estado"]
    faltantes = [x for x in requerido if x not in data]
    if faltantes:
        return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

    # Validar campos no vacíos (excepto contraseña que es opcional en edición)
    for campo in requerido:
        if str(data[campo]).strip() == "":
            return jsonify({"mensaje": f"El campo {campo} no puede estar vacío"}), 400

    # Validar longitud de campos de texto
    errores = validar_campos_texto(data, "usu_nombre", "usu_rol", "usu_correo", "usu_contrasena")
    if errores:
        return jsonify({"mensaje": " | ".join(errores)}), 400

    # Validar rol y estado
    roles_validos = ["Administrador", "Vendedor", "Bodeguero", "Contador"]
    if data["usu_rol"] not in roles_validos:
        return jsonify({"mensaje": f"Rol inválido"}), 400
    if data["usu_estado"] not in [0, 1]:
        return jsonify({"mensaje": "El estado debe ser 0 o 1"}), 400

    # Validar longitud mínima de contraseña (solo si se envía una nueva)
    if data.get("usu_contrasena") and len(str(data["usu_contrasena"]).strip()) < 6:
        return jsonify({"mensaje": "La contraseña debe tener al menos 6 caracteres"}), 400

    # Validar contraseña de administrador para autorizar cambios
    admin_pass = data.get("admin_contrasena")
    if not admin_pass or not admin_pass.strip():
        return jsonify({"mensaje": "Debes ingresar la contraseña de un administrador para autorizar los cambios"}), 401
    c = current_app.mysql.connection.cursor()
    c.execute("""
        SELECT u.usu_contrasena FROM t_usuario u
        INNER JOIN t_rol r ON u.usu_rol_id_fk = r.rol_id
        WHERE r.rol_nombre = 'Administrador'
    """)
    admin_hashes = [row[0] for row in c.fetchall()]
    c.close()
    from services.auth_service import verificarPassword
    autorizado = any(verificarPassword(admin_pass, h) for h in admin_hashes if h)
    if not autorizado:
        return jsonify({"mensaje": "Contraseña de administrador incorrecta. No tienes permisos para editar este usuario."}), 401

    # Normalizar correo a minúsculas
    data["usu_correo"] = (data.get("usu_correo") or "").strip().lower()

    # Verificar existencia y validar duplicidad de correo (que no sea de otro ID)
    c = current_app.mysql.connection.cursor()
    c.execute("SELECT usu_id FROM t_usuario WHERE usu_correo = %s AND usu_id != %s", (data["usu_correo"], data["usu_id"]))
    if c.fetchone():
        c.close()
        return jsonify({"mensaje": "El correo ya está en uso por otro usuario"}), 409
    c.close()

    resultado = editarUsuarios(
        data["usu_id"], data["usu_nombre"], data["usu_rol"],
        data["usu_correo"], data["usu_contrasena"], data["usu_estado"], data.get("usu_ultimo_acceso")
    )
    return jsonify({"mensaje": "Usuario actualizado correctamente", "datos": resultado}), 200


@safe_controller
def cneliminarusuarios(usu_id):
    # El usu_id viene de la URL, no del JSON
    usuario = buscarUsuarios(usu_id)
    if not usuario:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404

    try:
        eliminarUsuarios(usu_id)
        return jsonify({"mensaje": "Usuario eliminado", "id": usu_id}), 200
    except ValueError as e:
        return jsonify({"mensaje": str(e)}), 409
    except Exception as e:
        err_msg = str(e)
        # Error FK (MySQL 1451) — mostrar mensaje legible
        if "1451" in err_msg or "foreign key constraint" in err_msg.lower():
            return jsonify({"mensaje": "No se puede eliminar el usuario porque tiene registros asociados en el sistema (roles, pedidos, compras, etc.). Reasigne o elimine esos registros primero."}), 409
        return jsonify({"mensaje": f"Error al eliminar usuario: {err_msg}"}), 500
    
    
@safe_controller
def cnbuscarusuarios():
    # Obtenemos el ID desde los parámetros de la URL (Query String) ?usu_id=...
    usu_id = request.args.get("usu_id")
    
    if not usu_id:
        return jsonify({"mensaje": "Debe proporcionar un ID de usuario"}), 400

    usuario = buscarUsuarios(usu_id)
    
    if usuario:
        return jsonify(usuario), 200
    else:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404
