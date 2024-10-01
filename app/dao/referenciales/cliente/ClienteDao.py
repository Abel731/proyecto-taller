from flask import current_app as app
from app.conexion.Conexion import Conexion

class ClienteDao:

    def getClientes(self):
        clienteSQL = """
        SELECT id_cliente, id_persona, nombre, apellido, cedula, direccion, telefono, fecha_registro
        FROM clientes
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(clienteSQL)
            # trae datos de la bd
            lista_clientes = cur.fetchall()
            # retorno los datos
            lista_ordenada = []
            for item in lista_clientes:
                lista_ordenada.append({
                    "id_cliente": item[0],
                    "id_persona": item[1],  # Relación opcional
                    "nombre": item[2],
                    "apellido": item[3],
                    "cedula": item[4],
                    "direccion": item[5],
                    "telefono": item[6],
                    "fecha_registro": item[7]
                })
            return lista_ordenada
        except con.Error as e:
            app.logger.info(e)
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

    def guardarCliente(self, id_persona, nombre, apellido, cedula, direccion, telefono, fecha_registro):
        insertClienteSQL = """
        INSERT INTO clientes(id_persona, nombre, apellido, cedula, direccion, telefono, fecha_registro)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(insertClienteSQL, (id_persona, nombre, apellido, cedula, direccion, telefono, fecha_registro))
            # se confirma la insercion
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False

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
