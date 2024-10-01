from flask import current_app as app
from app.conexion.Conexion import Conexion

class DepositoDao:

    def getDepositos(self):
        depositoSQL = """
        SELECT id_deposito, nombre, direccion, telefono, capacidad
        FROM depositos
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(depositoSQL)
            # trae datos de la bd
            lista_depositos = cur.fetchall()
            # retorno los datos
            lista_ordenada = []
            for item in lista_depositos:
                lista_ordenada.append({
                    "id_deposito": item[0],
                    "nombre": item[1],
                    "direccion": item[2],
                    "telefono": item[3],
                    "capacidad": item[4],
                })
            return lista_ordenada
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

    def getDepositoById(self, id_deposito):
        depositoSQL = """
        SELECT id_deposito,  nombre, direccion, telefono, capacidad
        FROM depositos WHERE id_deposito=%s
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(depositoSQL, (id_deposito,))
            # trae datos de la bd
            depositoEncontrado = cur.fetchone()
            # retorno los datos
            if depositoEncontrado:
                return {
                    "id_deposito": depositoEncontrado[0],
                    "nombre": depositoEncontrado[1],
                    "direccion": depositoEncontrado[2],
                    "telefono": depositoEncontrado[3],
                    "capacidad": depositoEncontrado[4],
                }
            return None
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

    def guardarDeposito(self, nombre, direccion, telefono, capacidad):
        insertDepositoSQL = """
        INSERT INTO depositos(nombre, direccion, telefono, capacidad)
        VALUES (%s, %s, %s, %s)
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(insertDepositoSQL, (nombre, direccion, telefono, capacidad))
            # se confirma la insercion
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False

    def updateDeposito(self, id_deposito, nombre, direccion, telefono, capacidad):
        updateDepositoSQL = """
        UPDATE depositos
        SET nombre=%s, direccion=%s, telefono=%s, capacidad=%s
        WHERE id_deposito=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(updateDepositoSQL, (nombre, direccion, telefono, capacidad, id_deposito))
            # se confirma la insercion
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False

    def deleteDeposito(self, id_deposito):
        deleteDepositoSQL = """
        DELETE FROM depositos
        WHERE id_deposito=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(deleteDepositoSQL, (id_deposito,))
            # se confirma la insercion
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False
