from flask import Blueprint
from services.auth_service import token_requerido
from controllers.roles_controllers import cnListarRoles, cnRegistrarRoles, cnEditarRoles, cnEliminarRoles, cnBuscarRoles

roles_bp = Blueprint('roles', __name__)

@roles_bp.route('/', methods=["GET"])
@token_requerido
def listado():
    return cnListarRoles()

@roles_bp.route('/', methods=["POST"])
@token_requerido
def registrar():
    return cnRegistrarRoles()

@roles_bp.route('/', methods=["PUT"])
@token_requerido
def editar():
    return cnEditarRoles()

@roles_bp.route('/eliminar/<rol_id>', methods=["DELETE"])
@token_requerido
def eliminar(rol_id):
    return cnEliminarRoles(rol_id)

@roles_bp.route('/buscar', methods=["GET"])
@token_requerido
def buscar():
    return cnBuscarRoles()