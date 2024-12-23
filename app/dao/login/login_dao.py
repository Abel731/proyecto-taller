from app.conexion.Conexion import Conexion
from werkzeug.security import check_password_hash

def validar_usuario(usuario_input, clave_input):
    # Crear una instancia de la conexión
    conexion = Conexion()
    con = conexion.getConexion()

    # Crear un cursor para ejecutar la consulta
    cursor = con.cursor()

    try:
        # Realizar la consulta para obtener el usuario y la contraseña
        cursor.execute("""
            SELECT id_usuario, clave FROM usuarios WHERE usuario = %s
        """, (usuario_input,))
        usuario = cursor.fetchone()

        # Imprimir el resultado de la consulta
        print("Resultado de consulta de usuario:", usuario)

        # Si no se encuentra el usuario o la contraseña no coincide
        if not usuario:
            print("Usuario no encontrado.")
            return None
        if not check_password_hash(usuario[1], clave_input):
            print("Contraseña incorrecta para el usuario:", usuario_input)
            return None

        # Consultar los roles asociados al usuario
        cursor.execute("""
            SELECT r.nombre_rol FROM roles r
            JOIN usuario_roles ur ON r.id_rol = ur.id_rol
            WHERE ur.id_usuario = %s
        """, (usuario[0],))
        roles = cursor.fetchall()

        # Imprimir los roles asociados
        print("Roles asociados al usuario:", [r[0] for r in roles])

        # Devuelvo los datos del usuario y los roles
        return {
            'id_usuario': usuario[0],
            'usuario': usuario_input,
            'roles': [r[0] for r in roles]
        }

    except Exception as e:
        print(f"Error al validar el usuario: {e}")
        return None

    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        con.close()