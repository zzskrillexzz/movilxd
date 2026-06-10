from flask import Blueprint
from services.auth_service import token_requerido, rol_requerido
from controllers.pedidos_controllers import (
    cnlistadopedidos, cnregistrarpedidos, cnbuscarpedido,
    cneditarpedidos, cneliminarpedidos, cneverificarpago, cnnotificarpedido,
    cnsubircomprobante, cndescargarcomprobante, cnavanzarestado, cnenviarfactura
)

pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('/')
@token_requerido
def listado_pedidos():
    return cnlistadopedidos()

@pedidos_bp.route('/<string:id>', methods=["GET"])
@token_requerido
def buscar_pedido(id):
    return cnbuscarpedido(id)

@pedidos_bp.route('/', methods=["POST"])
@token_requerido
@rol_requerido('Administrador', 'Vendedor')
def registrar_pedidos():
    return cnregistrarpedidos()

@pedidos_bp.route('/<string:id>', methods=["PUT"])
@token_requerido
@rol_requerido('Administrador', 'Vendedor')
def editar_pedidos(id):
    return cneditarpedidos(id)

@pedidos_bp.route('/<string:id>/enviar-factura', methods=["POST"])
@token_requerido
@rol_requerido('Administrador', 'Vendedor')
def enviar_factura(id):
    return cnenviarfactura(id)

@pedidos_bp.route('/<string:id>/avanzar-estado', methods=["PUT"])
@token_requerido
@rol_requerido('Administrador', 'Vendedor')
def avanzar_estado(id):
    return cnavanzarestado(id)

@pedidos_bp.route('/<string:id>/comprobante', methods=["PUT"])
@token_requerido
@rol_requerido('Administrador', 'Vendedor')
def subir_comprobante(id):
    return cnsubircomprobante(id)

@pedidos_bp.route('/<string:id>/comprobante', methods=["GET"])
@token_requerido
def descargar_comprobante(id):
    return cndescargarcomprobante(id)

@pedidos_bp.route('/<string:id>/verificar-pago', methods=["PUT"])
@token_requerido
@rol_requerido('Administrador')
def verificar_pago_pedido(id):
    return cneverificarpago(id)

@pedidos_bp.route('/<string:id>/notificar', methods=["POST"])
@token_requerido
@rol_requerido('Administrador', 'Vendedor')
def notificar_pedido(id):
    return cnnotificarpedido(id)

@pedidos_bp.route('/<string:id>', methods=["DELETE"])
@token_requerido
@rol_requerido('Administrador')
def eliminar_pedidos(id):
    return cneliminarpedidos(id)