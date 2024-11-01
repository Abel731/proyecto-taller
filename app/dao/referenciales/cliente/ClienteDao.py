from flask import current_app as app
from app.conexion.Conexion import Conexion

class ClienteDao:

    def getClientes(self):
        clienteSQL = """
        SELECT 
            c.id_cliente
            , CONCAT(p.nombres, ' ', p.apellidos) AS cliente
            , p.ci
            , c.direccion
            , c.telefono
        FROM 
            clientes c
        LEFT JOIN 
        personas p ON p.id_persona = c.id_cliente;  
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(clienteSQL)
            lista_clientes = cur.fetchall()   # trae datos de la bd

            # Transformar los datos en una lista de diccionarios
            return [{'id_cliente': item[0], 'cliente': item[1], 'ci': item[2], 'direccion': item[3], 'telefono': item[4]} for item in lista_clientes]
        
        except con.Error as e:
            app.logger.info(e)(f"Error al obtener todos los clientes: {str(e)}")
        finally:
            cur.close()
            con.close()

    def getClienteById(self, id_cliente):
        clienteSQL = """
        SELECT id_cliente, id_persona, nombre, apellido, cedula, direccion, telefono, fecha_registro
        FROM clientes WHERE id_cliente=%s
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(clienteSQL, (id_cliente,))
            # trae datos de la bd
            clienteEncontrado = cur.fetchone()
            # retorno los datos
            if clienteEncontrado:
                return {
                    "id_cliente": clienteEncontrado[0],
                    "id_persona": clienteEncontrado[1],  # Relación opcional
                    "nombre": clienteEncontrado[2],
                    "apellido": clienteEncontrado[3],
                    "cedula": clienteEncontrado[4],
                    "direccion": clienteEncontrado[5],
                    "telefono": clienteEncontrado[6],
                    "fecha_registro": clienteEncontrado[7]
                }
            return None
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

    def guardarCliente(self, id_cliente,  direccion, telefono):
        insertClienteSQL = """
        INSERT INTO clientes(id_cliente,  direccion, telefono)
        VALUES (%s, %s, %s)
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(insertClienteSQL, (id_cliente, direccion, telefono))
            con.commit()
            return True  # Retorna True si la inserción fue exitosa
        except con.Error as e:
            app.logger.info(f"Error al guardar cliente: {str(e)}")
            return False  # Retorna False si hubo un error
        finally:
            cur.close()
            con.close()


    def updateCliente(self, id_cliente, nombre, apellido, cedula, direccion, telefono, fecha_registro):
        updateClienteSQL = """
        UPDATE clientes
        SET nombre=%s, apellido=%s, cedula=%s, direccion=%s, telefono=%s, fecha_registro=%s
        WHERE id_cliente=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(updateClienteSQL, (nombre, apellido, cedula, direccion, telefono, fecha_registro, id_cliente))
            # se confirma la insercion
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False

    def deleteCliente(self, id_cliente):
        deleteClienteSQL = """
        DELETE FROM clientes
        WHERE id_cliente=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(deleteClienteSQL, (id_cliente,))
            # se confirma la eliminación
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False
