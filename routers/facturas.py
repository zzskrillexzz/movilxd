from flask import Blueprint
from services.auth_service import token_requerido
from controllers.facturas_controllers import cnListarFacturas, cnRegistrarFacturas, cnEditarFacturas, cnEliminarFacturas, cnBuscarFacturas

facturas_bp = Blueprint('facturas', __name__)

@facturas_bp.route('/')
@token_requerido
def listado():
    return cnListarFacturas()

@facturas_bp.route('/', methods=["POST"])
@token_requerido
def registrar():
    return cnRegistrarFacturas()

@facturas_bp.route('/<fac_id>', methods=["PUT"])
@token_requerido
def editar(fac_id):
    return cnEditarFacturas(fac_id)

@facturas_bp.route('/<fac_id>', methods=["DELETE"])
@token_requerido
def eliminar(fac_id):
    return cnEliminarFacturas(fac_id)

@facturas_bp.route('/<fac_id>')
@token_requerido
def buscar(fac_id):
    return cnBuscarFacturas(fac_id)
