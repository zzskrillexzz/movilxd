from flask import Blueprint
from controllers.anulaciones_ventas_controllers import (
    cnlistadoanulacionesventas, cnregistraranulacionesventas,
    cneditaranulacionesventas, cneliminaranulacionesventas
)

anulaciones_ventas_bp = Blueprint('anulaciones_ventas', __name__)

@anulaciones_ventas_bp.route('/')
def listado():
    return cnlistadoanulacionesventas()

@anulaciones_ventas_bp.route('/', methods=["POST"])
def registrar():
    return cnregistraranulacionesventas()

@anulaciones_ventas_bp.route('/<string:id>', methods=["PUT"])
def editar(id):
    return cneditaranulacionesventas(id)

@anulaciones_ventas_bp.route('/<string:id>', methods=["DELETE"])
def eliminar(id):
    return cneliminaranulacionesventas(id)