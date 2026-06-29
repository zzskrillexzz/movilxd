"""Migración: cambia fac_fecha_emision de DATE a DATETIME (hora Colombia en facturas)"""
import MySQLdb

conn = MySQLdb.connect(host='localhost', user='root', port=3307, db='db_drogueria_sandiego', charset='utf8mb4')
c = conn.cursor()
try:
    c.execute("ALTER TABLE t_factura MODIFY COLUMN fac_fecha_emision DATETIME DEFAULT NULL COMMENT 'Fecha y hora de emisión (hora Colombia)'")
    conn.commit()
    print("✓ fac_fecha_emision cambiado de DATE a DATETIME")
except Exception as e:
    if 'Duplicate column' in str(e) or 'already' in str(e).lower():
        print("ℹ La columna ya es DATETIME, sin cambios")
    else:
        print(f"✗ Error: {e}")
        sys.exit(1)
finally:
    c.close()
    conn.close()
