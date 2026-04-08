from flask import jsonify,request
from services.detalles_de_pedido_service import listarDetallePedido, registrardetalledepedido

def cnlistadodet():
    try:
        obj = listarDetallePedido()
        return jsonify(obj),200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    
def cnregistrardetalle():
    # 1. Validación de campos presentes
    requerido = ["det_id", "det_cantidad", "det_subtotal"]
    
    faltantes = [x for x in requerido if x not in request.json]
    if faltantes:
        return jsonify({"mensaje": f"faltan los siguientes campos: {faltantes}"}), 400
    
    # 2. Extraer datos del JSON
    id_detalle = request.json["det_id"]
    cantidad = request.json["det_cantidad"]
    subtotal = request.json["det_subtotal"]

    # 3. Validación de campos vacíos o nulos
    if str(id_detalle).strip() == "":
        return jsonify({"mensaje": "El ID del detalle no puede estar vacío"}), 400

    # 4. Validación de tipos de datos y valores lógicos
    try:
        # Validar cantidad (que sea entero y mayor a 0)
        cant_num = int(cantidad)
        if cant_num <= 0:
            return jsonify({"mensaje": "La cantidad debe ser mayor a cero"}), 400
            
        # Validar subtotal (que sea número y no negativo)
        sub_num = float(subtotal)
        if sub_num < 0:
            return jsonify({"mensaje": "El subtotal no puede ser negativo"}), 400
            
    except ValueError:
        return jsonify({"mensaje": "La cantidad debe ser un número entero y el subtotal un número decimal"}), 400

    # 5. Si todo está correcto, llamar al service
    try:
        d = registrardetalledepedido(id_detalle, cantidad, subtotal)
        
        # Devolvemos éxito. 'd' ya es un diccionario porque lo corregimos en el service
        return jsonify({
            "mensaje": "detalle de pedido registrado correctamente", 
            "datos": d
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Error al guardar en base de datos: {str(e)}"}), 500