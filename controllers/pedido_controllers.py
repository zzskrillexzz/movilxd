from flask import jsonify, request
from services.pedido_service import listarPedido,registrarpedido

def cnlistadoped():
    try:
        x = listarPedido()
        return jsonify(x), 200
    
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    
    
def cnregistrarpedido():
    requerido = ["ped_id","ped_fecha", "ped_metodo_pago", "ped_estado_entrega","ped_cli_id_fk", "ped_det_id_fk"]
    
    faltantes = [x for x in requerido if x not in request.json]
    print(faltantes)
    if faltantes:
        return jsonify({"mensaje":f"faltan los siguientes campos {faltantes}"}),400
    
    id_pedido = request.json["ped_id"]
    fecha_pedido = request.json ["ped_fecha"]
    metodo_pago_pedido = request.json ["ped_metodo_pago"]
    estado_cliente = request.json ["ped_estado_entrega"]
    total_pedido = request.json ["ped_total"]
    fk_cliente = request.json ["ped_cli_id_fk"]
    fk_detalles = request.json ["ped_det_id_fk"]
    
    p = registrarpedido(id_pedido,fecha_pedido, metodo_pago_pedido, estado_cliente, total_pedido, fk_cliente, fk_detalles)
    
    return jsonify({"mensaje":"pedido realizado correctamente"}), 201