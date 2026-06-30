import MySQLdb
conn = MySQLdb.connect(host='localhost', user='root', port=3307, db='db_drogueria_sandiego')
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM t_monitoria m JOIN t_inventario_movimiento i ON i.inm_id=m.mon_inm_id_fk WHERE i.inm_id='INM080'")
print('Monitorias for INM080:', c.fetchone()[0])
c.execute('SELECT mon_id, mon_inm_id_fk, mon_tipo, mon_cantidad, mon_saldo_anterior, mon_saldo_actual FROM t_monitoria ORDER BY mon_fecha DESC LIMIT 5')
for r in c.fetchall():
    print(r)
c.close()
conn.close()
