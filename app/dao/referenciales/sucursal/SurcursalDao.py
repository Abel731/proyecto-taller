from flask import current_app as app
from app.conexion.Conexion import Conexion

class SucursalDao:

    def getSucursales(self):
        sucursalSQL = """
        SELECT id_sucursal, nombre, direccion, telefono
        FROM sucursales
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sucursalSQL)
            # trae datos de la bd
            lista_sucursales = cur.fetchall()
            # retorno los datos
            lista_ordenada = []
            for item in lista_sucursales:
                lista_ordenada.append({
                    "id_sucursal": item[0],
                    "nombre": item[1],
                    "direccion": item[2],
                    "telefono": item[3]  
                })
            return lista_ordenada
        except con.Error as e:
            app.logger.info(e)
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
