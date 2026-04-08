from flask import Blueprint
from controllers.detalle_de_pedido_controllers import cnlistadodet, cnregistrardetalle

detalles_bp = Blueprint('detalles',__name__)

@detalles_bp.route('/')
def listado():
    return cnlistadodet()

@detalles_bp.route('/', methods=["POST"])
def registrar():
    return cnregistrardetalle()