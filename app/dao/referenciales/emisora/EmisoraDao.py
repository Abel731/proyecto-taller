from flask import current_app as app
from app.conexion.Conexion import Conexion

class EmisoraDao:

    def getEmisoras(self):
        emisoraSQL = """
        SELECT id, descripcion
        FROM emisoras
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(emisoraSQL)
            lista_emisoras = cur.fetchall()
            lista_ordenada = []
            for item in lista_emisoras:
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

    def getEmisoraById(self, id):
        emisoraSQL = """
        SELECT id, descripcion
        FROM emisoras WHERE id=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(emisoraSQL, (id,))
            emisoraEncontrada = cur.fetchone()
            return {
                "id": emisoraEncontrada[0],
                "descripcion": emisoraEncontrada[1]
            }
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

    def guardarEmisora(self, descripcion):
        insertEmisoraSQL = """
        INSERT INTO emisoras(descripcion) VALUES(%s)
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(insertEmisoraSQL, (descripcion,))
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False

    def updateEmisora(self, id, descripcion):
        updateEmisoraSQL = """
        UPDATE emisoras
        SET descripcion=%s
        WHERE id=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(updateEmisoraSQL, (descripcion, id,))
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False

    def deleteEmisora(self, id):
        deleteEmisoraSQL = """
        DELETE FROM emisoras
        WHERE id=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(deleteEmisoraSQL, (id,))
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False
