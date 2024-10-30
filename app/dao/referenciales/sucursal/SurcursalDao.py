from flask import current_app as app
from app.conexion.Conexion import Conexion

class SucursalDao:

    def get_sucursales(self):

        sucursal_sql = """
        SELECT
            s.id_sucursal,
            s.descripcion AS nombre_sucursal
        FROM
            sucursales s
        WHERE
            EXISTS (
                SELECT 1
                FROM sucursal_depositos sd
                WHERE sd.id_sucursal = s.id_sucursal
            )
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sucursal_sql)
            sucursales = cur.fetchall() # trae datos de la bd

            # Transformar los datos en una lista de diccionarios
            return [{'id': sucursal[0], 'descripcion': sucursal[1]} for sucursal in sucursales]

        except Exception as e:
            app.logger.error(f"Error al obtener todas las sucursales: {str(e)}")
            return []

        finally:
            cur.close()
            con.close()

    def get_sucursal_depositos(self, id_sucursal: int):

        sucursal_sql = """
        SELECT
            sd.id_deposito
            , d.descripcion nombre_deposito
        FROM
            sucursal_depositos sd
        LEFT JOIN depositos d
            ON sd.id_deposito = d.id_deposito
        WHERE
            sd.id_sucursal = %s AND sd.estado = true
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sucursal_sql, (id_sucursal,))
            sucursales = cur.fetchall() # trae datos de la bd

            # Transformar los datos en una lista de diccionarios
            return [{'id_deposito': sucursal[0], 'nombre_deposito': sucursal[1]} for sucursal in sucursales]

        except Exception as e:
            app.logger.error(f"Error al obtener las sucursales con depositos: {str(e)}")
            return []

        finally:
            cur.close()
            con.close()

    def getSucursalById(self, id_sucursal):
        sucursalSQL = """
        SELECT id_sucursal, nombre, direccion, telefono
        FROM sucursales WHERE id_sucursal=%s
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sucursalSQL, (id_sucursal,))
            # trae datos de la bd
            sucursalEncontrada = cur.fetchone()
            # retorno los datos
            if sucursalEncontrada:
                return {
                    "id_sucursal": sucursalEncontrada[0],
                    "nombre": sucursalEncontrada[1],
                    "direccion": sucursalEncontrada[2],
                    "telefono": sucursalEncontrada[3]  
                }
            return None
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

    def guardarSucursal(self, nombre, direccion, telefono):
        insertSucursalSQL = """
        INSERT INTO sucursales(nombre, direccion, telefono)
        VALUES (%s, %s, %s)
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(insertSucursalSQL, (nombre, direccion, telefono))
            # se confirma la insercion
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False

    def updateSucursal(self, id_sucursal, nombre, direccion, telefono):
        updateSucursalSQL = """
        UPDATE sucursales
        SET nombre=%s, direccion=%s, telefono=%s
        WHERE id_sucursal=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(updateSucursalSQL, (nombre, direccion, telefono, id_sucursal))  
            # se confirma la insercion
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False

    def deleteSucursal(self, id_sucursal):
        deleteSucursalSQL = """
        DELETE FROM sucursales
        WHERE id_sucursal=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(deleteSucursalSQL, (id_sucursal,))
            # se confirma la insercion
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False
