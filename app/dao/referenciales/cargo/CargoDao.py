from flask import current_app as app
from app.conexion.Conexion import Conexion

class CargoDao:

    def getCargos(self):
        cargoSQL = """
        SELECT id, descripcion
        FROM cargos
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(cargoSQL)
            # trae datos de la bd
            lista_cargos = cur.fetchall()
            # retorno los datos
            lista_ordenada = []
            for item in lista_cargos:
                lista_ordenada.append({
                    "id": item[0],
                    "descripcion": item[1]
                })
            return lista_ordenada
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

    def getCargoById(self, id):
        cargoSQL = """
        SELECT id, descripcion
        FROM cargos WHERE id=%s
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(cargoSQL, (id,))
            # trae datos de la bd
            cargoEncontrado = cur.fetchone()
            # retorno los datos
            if cargoEncontrado:
                return {
                    "id": cargoEncontrado[0],
                    "descripcion": cargoEncontrado[1]
                }
            return None
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

    def guardarCargo(self, descripcion):
        insertCargoSQL = """
        INSERT INTO cargos(descripcion) VALUES(%s)
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(insertCargoSQL, (descripcion,))
            # se confirma la insercion
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False

    def updateCargo(self, id, descripcion):
        updateCargoSQL = """
        UPDATE cargos
        SET descripcion=%s
        WHERE id=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(updateCargoSQL, (descripcion, id,))
            # se confirma la insercion
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False

    def deleteCargo(self, id):
        deleteCargoSQL = """
        DELETE FROM cargos
        WHERE id=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(deleteCargoSQL, (id,))
            # se confirma la insercion
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False
