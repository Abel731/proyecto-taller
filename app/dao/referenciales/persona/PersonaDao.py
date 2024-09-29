from flask import current_app as app
from app.conexion.Conexion import Conexion

class PersonaDao:

    def getPersonas(self):
        personaSQL = """
        SELECT id_persona, nombres, apellidos, nro_cedula, fecha_nacimiento, direccion
        FROM personas
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(personaSQL)
            # trae datos de la bd
            lista_personas = cur.fetchall()
            # retorno los datos
            lista_ordenada = []
            for item in lista_personas:
                lista_ordenada.append({
                    "id_persona": item[0],
                    "nombres": item[1],
                    "apellidos": item[2],
                    "nro_cedula": item[3],
                    "fecha_nacimiento": item[4],
                    "direccion": item[5]
                })
            return lista_ordenada
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

    def getPersonaById(self, id_persona):
        personaSQL = """
        SELECT id_persona, nombres, apellidos, nro_cedula, fecha_nacimiento, direccion
        FROM personas WHERE id_persona=%s
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(personaSQL, (id_persona,))
            # trae datos de la bd
            personaEncontrada = cur.fetchone()
            # retorno los datos
            if personaEncontrada:
                return {
                    "id_persona": personaEncontrada[0],
                    "nombres": personaEncontrada[1],
                    "apellidos": personaEncontrada[2],
                    "nro_cedula": personaEncontrada[3],
                    "fecha_nacimiento": personaEncontrada[4],
                    "direccion": personaEncontrada[5]
                }
            return None
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

    def guardarPersona(self, nombres, apellidos, nro_cedula, fecha_nacimiento, direccion):
        insertPersonaSQL = """
        INSERT INTO personas(nombres, apellidos, nro_cedula, fecha_nacimiento, direccion)
        VALUES (%s, %s, %s, %s, %s)
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(insertPersonaSQL, (nombres, apellidos, nro_cedula, fecha_nacimiento, direccion))
            # se confirma la insercion
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False

    def updatePersona(self, id_persona, nombres, apellidos, nro_cedula, fecha_nacimiento, direccion):
        updatePersonaSQL = """
        UPDATE personas
        SET nombres=%s, apellidos=%s, nro_cedula=%s, fecha_nacimiento=%s, direccion=%s
        WHERE id_persona=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(updatePersonaSQL, (nombres, apellidos, nro_cedula, fecha_nacimiento, direccion, id_persona))
            # se confirma la insercion
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False

    def deletePersona(self, id_persona):
        deletePersonaSQL = """
        DELETE FROM personas
        WHERE id_persona=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(deletePersonaSQL, (id_persona,))
            # se confirma la insercion
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False
