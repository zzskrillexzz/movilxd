from flask import Blueprint
from services.auth_service import token_requerido
from controllers.lotes_controllers import cnlistadolotes, cnregistrarlotes, cnEditarlotes

lotes_bp = Blueprint('lotes', __name__)

@lotes_bp.route('/')
@token_requerido
def listado():
    return cnlistadolotes()

@lotes_bp.route('/', methods=["POST"])
@token_requerido
def registrar():
    return cnregistrarlotes()

@lotes_bp.route('/', methods=["PUT"])
@token_requerido
def editar():
    return cnEditarlotes()