from flask import Blueprint, jsonify
from controllers.pedidos_controllers import cnconfirmarentrega

publico_bp = Blueprint('publico', __name__)

@publico_bp.route('/')
def index():
    return jsonify({"mensaje": "API San Diego Distribuidora - Sistema de Pedidos", "estado": "online"}), 200

@publico_bp.route('/verificar/<pedido_id>')
def verificar_estado(pedido_id):
    """Endpoint público para verificar estado de un pedido (útil para depuración)."""
    from services.pedidos_service import buscarPedido
    pedido = buscarPedido(pedido_id)
    if not pedido:
        return jsonify({"error": "Pedido no encontrado"}), 404
    return jsonify({
        "ped_id": pedido.get("ped_id"),
        "ped_estado_entrega": pedido.get("ped_estado_entrega"),
        "ped_estado_pago": pedido.get("ped_estado_pago"),
        "ped_token_entrega": pedido.get("ped_token_entrega")
    }), 200

@publico_bp.route('/confirmar-entrega/<token>', methods=['GET', 'POST'])
def confirmar_entrega(token):
    return cnconfirmarentrega(token)
