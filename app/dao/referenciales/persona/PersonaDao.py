from flask import current_app as app
from app.conexion.Conexion import Conexion
from datetime import datetime, time

class PersonaDao:

    def getPersonas(self):
        personaSQL = """
        SELECT id_persona, nombres, apellidos, ci, fechanac, creacion_fecha, creacion_hora, creacion_usuario
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
                    "ci": item[3],
                    "fechanac": item[4].strftime('%Y-%m-%d') if isinstance(item[4], datetime) else item[4],
                    "creacion_fecha": item[5],
                    "creacion_hora": item[6].strftime('%H:%M:%S') if isinstance(item[6], time) else item[6],
                    "creacion_usuario": item[7]
                })
            return lista_ordenada
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

    def getPersonaById(self, id_persona):
        personaSQL = """
        SELECT id_persona, nombres, apellidos, ci, fechanac, creacion_fecha, creacion_hora, creacion_usuario
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
                    "ci": personaEncontrada[3],
                    "fechanac": personaEncontrada[4].strftime('%Y-%m-%d') if isinstance(personaEncontrada[4], datetime) else personaEncontrada[4],
                    "creacion_fecha": personaEncontrada[5],
                    "creacion_hora": personaEncontrada[6].strftime('%H:%M:%S') if isinstance(personaEncontrada[6], time) else personaEncontrada[6],
                    "creacion_usuario": personaEncontrada[7]
                }
            return None
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

    def guardarPersona(self, nombres, apellidos, ci, fechanac, creacion_fecha, creacion_hora, creacion_usuario):
        insertPersonaSQL = """
        INSERT INTO personas(nombres, apellidos, ci, fechanac, creacion_fecha, creacion_hora, creacion_usuario)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(insertPersonaSQL, (nombres, apellidos, ci, fechanac, creacion_fecha, creacion_hora, creacion_usuario))
            # se confirma la insercion
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False

    def updatePersona(self, id_persona, nombres, apellidos, ci, fechanac, creacion_fecha, creacion_hora, creacion_usuario):
        updatePersonaSQL = """
        UPDATE personas
        SET nombres=%s, apellidos=%s, ci=%s, fechanac=%s, creacion_fecha=%s, creacion_hora=%s, creacion_usuario=%s
        WHERE id_persona=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(updatePersonaSQL, (nombres, apellidos, ci, fechanac, creacion_fecha, creacion_hora, creacion_usuario, id_persona))
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
