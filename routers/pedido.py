from flask import Blueprint
from controllers.pedido_controllers import cnlistadoped,cnregistrarpedido

pedido_bp = Blueprint('pedidos', __name__)

@pedido_bp.route('/')
def listado_ped():
    return cnlistadoped()

@pedido_bp.route('/', methods=["POST"])
def registrarpedido():
    return cnregistrarpedido()