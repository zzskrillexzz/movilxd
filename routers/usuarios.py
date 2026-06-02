from flask import Blueprint
from services.auth_service import token_requerido, rol_requerido
from controllers.usuarios_controllers import cnlistadousuarios, cnregistrarusuarios, cneliminarusuarios, cnbuscarusuarios, cneditarusuarios

usuarios_bp = Blueprint('usuarios', __name__)

# Listar todos los usuarios
@usuarios_bp.route('/', methods=["GET"])
@token_requerido
def listado():
    return cnlistadousuarios()

# Registrar un nuevo usuario
@usuarios_bp.route('/', methods=["POST"])
@token_requerido
@rol_requerido('Administrador')
def registrar():
    return cnregistrarusuarios()

# Editar un usuario existente
@usuarios_bp.route('/', methods=["PUT"])
@token_requerido
@rol_requerido('Administrador')
def editar():
    return cneditarusuarios()

# Eliminar un usuario
@usuarios_bp.route('/eliminar/<usu_id>', methods=["DELETE"])
@token_requerido
@rol_requerido('Administrador')
def eliminar(usu_id):
    return cneliminarusuarios(usu_id)

@usuarios_bp.route('/buscar', methods=["GET"])
@token_requerido
def buscar():
    return cnbuscarusuarios()