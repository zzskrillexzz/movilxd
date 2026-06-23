from flask import jsonify, request, send_file
from services.reportes_service import (
    listarReportes, registrarReportes, editarReportes, eliminarReportes, buscarReportes,
    reporte_ventas, reporte_inventario, reporte_mas_vendidos, reporte_por_vencer,
    exportar_reporte_pdf, exportar_reporte_excel
)
from utils.error_handler import safe_controller
from io import BytesIO
from datetime import date

@safe_controller
def cnlistarreportes():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    q = request.args.get('q', None)
    order_by = request.args.get('order_by', None)
    filtros = {k: v for k, v in request.args.items() if k not in ('page', 'limit', 'q', 'order_by')}
    datos = listarReportes(page=page, limit=limit, q=q, order_by=order_by, **filtros)
    return jsonify(datos), 200

@safe_controller
def cnregistrarreportes():
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

    requerido = ["rep_id", "rep_tipo", "rep_fecha", "rep_parametros", "rep_usu_id_fk"]
    faltantes = [x for x in requerido if x not in data]
    if faltantes:
        return jsonify({"mensaje": f"Faltan los siguientes campos: {faltantes}"}), 400

    resultado = registrarReportes(
        data["rep_id"], data["rep_tipo"], data["rep_fecha"],
        data["rep_parametros"], data["rep_usu_id_fk"], data.get("rep_resultado")
    )
    return jsonify({"mensaje": "Reporte registrado", "datos": resultado}), 201

@safe_controller
def cneditarreportes():
    data = request.get_json()
    if not data or "rep_id" not in data:
        return jsonify({"mensaje": "ID de reporte requerido"}), 400

    resultado = editarReportes(
        data["rep_id"], data.get("rep_tipo"), data.get("rep_fecha"),
        data.get("rep_parametros"), data.get("rep_usu_id_fk"), data.get("rep_resultado")
    )
    return jsonify({"mensaje": "Reporte actualizado", "datos": resultado}), 200

@safe_controller
def cneliminarreportes(rep_id):
    if not buscarReportes(rep_id):
        return jsonify({"mensaje": "Reporte no encontrado"}), 404
    return jsonify(eliminarReportes(rep_id)), 200

@safe_controller
def cnbuscarreportes():
    rep_id = request.args.get("rep_id")
    resultado = buscarReportes(rep_id)
    if resultado:
        return jsonify(resultado), 200
    return jsonify({"mensaje": "Reporte no encontrado"}), 404


# ═══════════════════════════════════════════════════════════════════
#  REPORTES REALES (agregaciones de negocio)
# ═══════════════════════════════════════════════════════════════════

@safe_controller
def cngenerar_reporte(tipo):
    """Endpoint unificado: GET /reportes/generar/<tipo>?fecha_desde=...&fecha_hasta=..."""
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')

    if tipo == 'ventas':
        datos = reporte_ventas(fecha_desde, fecha_hasta)
    elif tipo == 'inventario':
        datos = reporte_inventario()
    elif tipo == 'mas_vendidos':
        datos = reporte_mas_vendidos(fecha_desde, fecha_hasta)
    elif tipo == 'por_vencer':
        dias = request.args.get('dias', 30, type=int)
        datos = reporte_por_vencer(dias)
    else:
        return jsonify({"mensaje": f"Tipo de reporte desconocido: {tipo}"}), 400

    return jsonify({"tipo": tipo, "total": len(datos), "datos": datos}), 200


@safe_controller
def cnexportar_reporte(tipo, formato):
    """
    Exporta un reporte en PDF o Excel.
    GET /reportes/exportar/<tipo>/<formato>?fecha_desde=...&fecha_hasta=...&dias=...
    """
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    dias = request.args.get('dias', 30, type=int)

    if formato == 'pdf':
        pdf_bytes = exportar_reporte_pdf(tipo, fecha_desde, fecha_hasta, dias)
        if pdf_bytes is None:
            return jsonify({"mensaje": f"Tipo de reporte desconocido: {tipo}"}), 400
        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"reporte_{tipo}_{date.today().isoformat()}.pdf"
        )
    elif formato == 'excel':
        xlsx_bytes = exportar_reporte_excel(tipo, fecha_desde, fecha_hasta, dias)
        if xlsx_bytes is None:
            return jsonify({"mensaje": f"Tipo de reporte desconocido: {tipo}"}), 400
        return send_file(
            BytesIO(xlsx_bytes),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"reporte_{tipo}_{date.today().isoformat()}.xlsx"
        )
    else:
        return jsonify({"mensaje": f"Formato desconocido: {formato}. Use 'pdf' o 'excel'"}), 400
