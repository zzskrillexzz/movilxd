import bcrypt
import MySQLdb

salt = bcrypt.gensalt()
pwd_hash = bcrypt.hashpw(b'test123', salt).decode()

conn = MySQLdb.connect(host='localhost', user='root', port=3307, db='db_drogueria_sandiego')
c = conn.cursor()
try:
    c.execute("INSERT INTO t_usuario (usu_id, usu_nombre, usu_correo, usu_contrasena, usu_rol_id_fk, usu_estado) VALUES (%s, %s, %s, %s, %s, %s)",
              ('USU200', 'Test Admin', 'test@test.com', pwd_hash, 'ROL001', 'Activo'))
    conn.commit()
    print("Usuario creado: test@test.com / test123")
except Exception as e:
    print(f"Error: {e}")
finally:
    c.close()
    conn.close()
