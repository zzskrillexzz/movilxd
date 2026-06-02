"""
Respuestas HTTP estandarizadas para toda la API.
BUG-017: Unificar formato de respuesta.

Uso:
    from utils.responses import ok, error
    
    return ok({"id": "USU001", "nombre": "Admin"})
    return error("Credenciales incorrectas", code=401)
    return error("No encontrado", detalle="Usuario no existe", code=404)
"""

from flask import jsonify
import os


def ok(data=None, mensaje="Operación exitosa", code=200):
    """
    Respuesta exitosa estandarizada.
    
    Args:
        data: Datos a retornar (dict o list, opcional)
        mensaje: Mensaje descriptivo
        code: Código HTTP (default 200)
    """
    body = {
        "success": True,
        "mensaje": mensaje,
    }
    if data is not None:
        body["data"] = data
    
    response = jsonify(body)
    response.status_code = code
    return response


def error(mensaje="Error interno del servidor", detalle=None, code=500):
    """
    Respuesta de error estandarizada.
    
    Args:
        mensaje: Mensaje de error público
        detalle: Detalle técnico (se omite en producción)
        code: Código HTTP (default 500)
    """
    es_produccion = os.getenv('FLASK_ENV', 'development') == 'production'
    
    body = {
        "success": False,
        "error": mensaje,
    }
    
    # En desarrollo incluimos detalle; en producción solo si se explicitó
    if detalle and not es_produccion:
        body["detalle"] = detalle
    elif detalle and es_produccion:
        # En producción, log interno (el detalle no se expone al cliente)
        pass
    
    response = jsonify(body)
    response.status_code = code
    return response


def created(data=None, mensaje="Recurso creado exitosamente"):
    """Atajo para 201 Created."""
    return ok(data=data, mensaje=mensaje, code=201)


def no_content():
    """Atajo para 204 No Content."""
    response = jsonify({})
    response.status_code = 204
    return response
