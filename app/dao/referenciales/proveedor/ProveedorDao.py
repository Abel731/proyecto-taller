from flask import current_app as app
from app.conexion.Conexion import Conexion

class ProveedorDao:

    def get_proveedores(self):

        prov_sql = """
        SELECT
            prov.id_proveedor
            , prov.ruc
            , prov.razon_social
        FROM proveedores prov
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(prov_sql)
            proveedores = cur.fetchall() # trae datos de la bd

            # Transformar los datos en una lista de diccionarios
            return [{'id_proveedor': proveedor[0], 'ruc': proveedor[1], 'razon_social': proveedor[2]} for proveedor in proveedores]

        except Exception as e:
            app.logger.error(f"Error al obtener todos los proveedores: {str(e)}")
            return []

        finally:
            cur.close()
            con.close()



    def getProveedores(self):
        proveedorSQL = """
        SELECT id_proveedor, ruc, razon_social, direccion, telefono
        FROM proveedores
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(proveedorSQL)
            # trae datos de la bd
            lista_proveedores = cur.fetchall()
            # retorno los datos
            lista_ordenada = []
            for item in lista_proveedores:
                lista_ordenada.append({
                    "id_proveedor": item[0],
                    "ruc": item[1],
                    "razon_social": item[2],
                    "direccion": item[3],
                    "telefono": item[4]  
                })
            return lista_ordenada
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

    def getProveedorById(self, id_proveedor):
        proveedorSQL = """
        SELECT id_proveedor, ruc, razon_social, direccion, telefono
        FROM proveedores WHERE id_proveedor=%s
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(proveedorSQL, (id_proveedor,))
            # trae datos de la bd
            proveedorEncontrado = cur.fetchone()
            # retorno los datos
            if proveedorEncontrado:
                return {
                    "id_proveedor": proveedorEncontrado[0],
                    "ruc": proveedorEncontrado[1],
                    "razon_social": proveedorEncontrado[2],
                    "direccion": proveedorEncontrado[3],
                    "telefono": proveedorEncontrado[4]  
                }
            return None
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

    def guardarProveedor(self, ruc, razon_social, direccion, telefono):
        insertProveedorSQL = """
        INSERT INTO proveedores(ruc, razon_social, direccion, telefono)
        VALUES (%s, %s, %s, %s)
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(insertProveedorSQL, (ruc, razon_social, direccion, telefono))
            # se confirma la insercion
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False

    def updateProveedor(self, id_proveedor, ruc, razon_social, direccion, telefono):
        updateProveedorSQL = """
        UPDATE proveedores
        SET ruc=%s, razon_social=%s, direccion=%s, telefono=%s
        WHERE id_proveedor=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(updateProveedorSQL, (ruc, razon_social, direccion, telefono, id_proveedor))
            # se confirma la insercion
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False

    def deleteProveedor(self, id_proveedor):
        deleteProveedorSQL = """
        DELETE FROM proveedores
        WHERE id_proveedor=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(deleteProveedorSQL, (id_proveedor,))
            # se confirma la eliminación
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False
