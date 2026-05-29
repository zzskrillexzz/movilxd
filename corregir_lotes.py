"""
Script para corregir lot_numero de todos los lotes según su producto.
Ejecutar: python corregir_lotes.py
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, mysql

with app.app_context():
    cur = mysql.connection.cursor()
    
    # Obtener todos los lotes ordenados
    cur.execute("""
        SELECT l.lot_id, l.lot_pro_id_fk, l.lot_fecha_fabricacion, p.pro_nombre
        FROM t_lote l
        JOIN t_producto p ON l.lot_pro_id_fk = p.pro_id
        ORDER BY l.lot_pro_id_fk, l.lot_id ASC
    """)
    
    lotes = cur.fetchall()
    contadores = {}
    actualizados = []
    
    for lot_id, pro_id, fecha_fab, pro_nombre in lotes:
        abrev = pro_nombre[:3].upper() if pro_nombre else 'XXX'
        anio = str(fecha_fab.year) if fecha_fab else '2025'
        clave = f"{abrev}-{anio}"
        contadores[clave] = contadores.get(clave, 0) + 1
        seq = str(contadores[clave]).zfill(3)
        nuevo = f"LT-{abrev}-{anio}-{seq}"
        
        cur.execute("UPDATE t_lote SET lot_numero = %s WHERE lot_id = %s", (nuevo, lot_id))
        actualizados.append(f"{lot_id}: {pro_nombre} → {nuevo}")
    
    mysql.connection.commit()
    cur.close()
    
    print("✅ lot_numero corregidos:")
    for a in actualizados:
        print(f"   {a}")

print("\nListo. Recarga la página de Inventario.")
