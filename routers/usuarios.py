from flask import Blueprint
from controllers.usuarios_controllers import cnlistadousuarios, cnregistrarusuarios, cneliminarusuarios, cnbuscarusuarios, cneditarusuarios

usuarios_bp = Blueprint('usuarios', __name__)

# Listar todos los usuarios
@usuarios_bp.route('/', methods=["GET"])
def listado():
    return cnlistadousuarios()

# Registrar un nuevo usuario
@usuarios_bp.route('/', methods=["POST"])
def registrar():
    return cnregistrarusuarios()

# Editar un usuario existente
@usuarios_bp.route('/', methods=["PUT"])
def editar():
    return cneditarusuarios()

# Eliminar un usuario
@usuarios_bp.route('/eliminar/<usu_id>', methods=["DELETE"])
def eliminar(usu_id):
    return cneliminarusuarios(usu_id)

@usuarios_bp.route('/buscar', methods=["GET"])
def buscar():
    return cnbuscarusuarios()