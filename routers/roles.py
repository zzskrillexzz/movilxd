from flask import Blueprint
from controllers.roles_controllers import cnListarRoles, cnRegistrarRoles, cnEditarRoles, cnEliminarRoles, cnBuscarRoles

roles_bp = Blueprint('roles', __name__)

@roles_bp.route('/', methods=["GET"])
def listado():
    return cnListarRoles()

@roles_bp.route('/', methods=["POST"])
def registrar():
    return cnRegistrarRoles()

@roles_bp.route('/', methods=["PUT"])
def editar():
    return cnEditarRoles()

@roles_bp.route('/eliminar/<rol_id>', methods=["DELETE"])
def eliminar(rol_id):
    return cnEliminarRoles(rol_id)

@roles_bp.route('/buscar', methods=["GET"])
def buscar():
    return cnBuscarRoles()