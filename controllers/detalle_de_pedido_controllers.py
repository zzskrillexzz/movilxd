from flask import jsonify,request
from services.detalles_de_pedido_service import listarDetallePedido

def cnlistadodet():
    try:
        obj = listarDetallePedido()
        return jsonify(obj),200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    