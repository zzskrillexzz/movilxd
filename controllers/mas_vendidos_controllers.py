from flask import jsonify
from services.mas_vendidos_service import listarMasVendidos

def cnlistadomasvendidos():
    try:
        return jsonify(listarMasVendidos()), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500