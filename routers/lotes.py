from datetime import date
from flask import Blueprint, jsonify, current_app
from services.auth_service import token_requerido, rol_requerido
from controllers.lotes_controllers import cnlistadolotes, cnregistrarlotes, cnEditarlotes, cnEliminarLotes
from utils.error_handler import safe_controller

lotes_bp = Blueprint('lotes', __name__)

@lotes_bp.route('/')
@token_requerido
def listado():
    return cnlistadolotes()

@lotes_bp.route('/', methods=["POST"])
@token_requerido
@rol_requerido('Administrador', 'Bodeguero')
def registrar():
    return cnregistrarlotes()

@lotes_bp.route('/', methods=["PUT"])
@token_requerido
@rol_requerido('Administrador', 'Bodeguero')
def editar():
    return cnEditarlotes()

@lotes_bp.route('/<id>', methods=["DELETE"])
@token_requerido
def eliminar(id):
    return cnEliminarLotes(id)

# ── Endpoint UNA SOLA VEZ: renumerar lotes secuencialmente ──
@lotes_bp.route('/renumerar', methods=["POST"])
@token_requerido
def renumerar_lotes():
    """
    Renumera todos los lotes existentes con IDs secuenciales (LOT001, LOT002...)
    y actualiza todas las FK en las tablas relacionadas.
    """
    try:
        c = current_app.mysql.connection.cursor()

        # 1. Obtener IDs actuales ordenados
        c.execute("SELECT lot_id FROM t_lote ORDER BY CAST(SUBSTRING(lot_id, 4) AS UNSIGNED) ASC")
        old_ids = [row[0] for row in c.fetchall()]

        # 2. Crear mapping old → new
        mapping = {}
        for i, old_id in enumerate(old_ids):
            new_id = f'LOT{str(i + 1).zfill(3)}'
            mapping[old_id] = new_id

        # 3. Actualizar cada tabla
        updates = []

        for old_id, new_id in mapping.items():
            if old_id == new_id:
                continue
            c.execute("UPDATE t_lote SET lot_id = %s WHERE lot_id = %s", (new_id, old_id))
            c.execute("UPDATE t_alerta_vencimiento SET alv_lot_id_fk = %s WHERE alv_lot_id_fk = %s", (new_id, old_id))
            c.execute("UPDATE t_detalle_compra SET dco_lot_id_fk = %s WHERE dco_lot_id_fk = %s", (new_id, old_id))
            c.execute("UPDATE t_inventario_movimiento SET inm_lot_id_fk = %s WHERE inm_lot_id_fk = %s", (new_id, old_id))
            c.execute("UPDATE t_monitoria SET mon_lot_id_fk = %s WHERE mon_lot_id_fk = %s", (new_id, old_id))
            c.execute("UPDATE t_detalle_pedido SET det_lot_id_fk = %s WHERE det_lot_id_fk = %s", (new_id, old_id))
            c.execute("UPDATE t_devolucion SET dev_lot_id_fk = %s WHERE dev_lot_id_fk = %s", (new_id, old_id))
            updates.append({'old_id': old_id, 'new_id': new_id})

        current_app.mysql.connection.commit()
        c.close()

        # 4. Mostrar resultado
        c2 = current_app.mysql.connection.cursor()
        c2.execute("SELECT lot_id, lot_numero, lot_pro_id_fk FROM t_lote ORDER BY lot_id")
        result = c2.fetchall()
        c2.close()

        return jsonify({
            "mensaje": f"Renumeración completada: {len(updates)} lotes actualizados",
            "cambios": updates,
            "lotes": [{"lot_id": r[0], "lot_numero": r[1], "producto": r[2]} for r in result]
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error en la renumeración: {str(e)}"}), 500


# ── Endpoint: corregir lot_numero según el producto de cada lote ──
@lotes_bp.route('/corregir-numeros', methods=["POST"])
@token_requerido
def corregir_numeros_lotes():
    """
    Recalcula el campo lot_numero de todos los lotes según el producto asociado.
    Formato: LT-{ABREV}-{AÑO}-{SEQ}  ej: LT-ACE-2025-001
    """
    try:
        c = current_app.mysql.connection.cursor()

        # Obtener todos los lotes ordenados por producto y ID
        c.execute("""
            SELECT l.lot_id, l.lot_pro_id_fk, l.lot_fecha_vencimiento, p.pro_nombre
            FROM t_lote l
            JOIN t_producto p ON l.lot_pro_id_fk = p.pro_id
            ORDER BY l.lot_pro_id_fk, l.lot_id ASC
        """)
        lotes_data = c.fetchall()

        actualizados = []
        prod_anterior = None
        contador_por_prod = {}

        for lot_id, pro_id, fecha_ven, pro_nombre in lotes_data:
            abrev = pro_nombre[:3].upper() if pro_nombre else 'XXX'
            anio = str(fecha_ven.year) if fecha_ven else str(date.today().year)

            clave = f"{abrev}-{anio}"
            contador_por_prod[clave] = contador_por_prod.get(clave, 0) + 1
            seq = str(contador_por_prod[clave]).zfill(3)

            nuevo_numero = f"LT-{abrev}-{anio}-{seq}"

            c.execute("UPDATE t_lote SET lot_numero = %s WHERE lot_id = %s", (nuevo_numero, lot_id))
            actualizados.append({"lot_id": lot_id, "producto": pro_nombre, "nuevo_numero": nuevo_numero})

        current_app.mysql.connection.commit()
        c.close()

        return jsonify({
            "mensaje": f"Corregidos {len(actualizados)} lotes",
            "detalle": actualizados
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500