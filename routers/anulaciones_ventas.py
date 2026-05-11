from flask import Blueprint
from services.auth_service import token_requerido
from controllers.anulaciones_ventas_controllers import (
    cnlistadoanulacionesventas, cnregistraranulacionesventas,
    cneditaranulacionesventas, cneliminaranulacionesventas
)

anulaciones_ventas_bp = Blueprint('anulaciones_ventas', __name__)

@anulaciones_ventas_bp.route('/')
@token_requerido
def listado():
    return cnlistadoanulacionesventas()

@anulaciones_ventas_bp.route('/', methods=["POST"])
@token_requerido
def registrar():
    return cnregistraranulacionesventas()

@anulaciones_ventas_bp.route('/<string:id>', methods=["PUT"])
@token_requerido
def editar(id):
    return cneditaranulacionesventas(id)

@anulaciones_ventas_bp.route('/<string:id>', methods=["DELETE"])
@token_requerido
def eliminar(id):
    return cneliminaranulacionesventas(id)