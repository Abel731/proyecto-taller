from flask import current_app as app
from app.conexion.Conexion import Conexion

class ProductoDao:

    def get_productos(self):

        sucursal_sql = """
        SELECT
            id_producto
            , nombre
            , cantidad
            , precio_unitario
        FROM
            public.productos
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sucursal_sql)
            productos = cur.fetchall() # trae datos de la bd

            # Transformar los datos en una lista de diccionarios
            return [{'id_producto': item[0], 'nombre': item[1]\
                , 'cantidad': item[2], 'precio_unitario': item[3]} for item in productos]

        except Exception as e:
            app.logger.error(f"Error al obtener todas las productos: {str(e)}")
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

    def getProductoById(self, id):

        productoSQL = """
        SELECT id, descripcion, cantidad, precio_unitario
        FROM productos WHERE id=%s
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(productoSQL, (id,))
            # trae datos de la bd
            productoEncontrado = cur.fetchone()
            # retorno los datos
            return {
                    "id": productoEncontrado[0],
                    "descripcion": productoEncontrado[1],
                    "cantidad": productoEncontrado[2],
                    "precio_unitario": productoEncontrado[3]
                }
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

    def guardarProducto(self, descripcion, cantidad, precio_unitario):

        insertProductoSQL = """
        INSERT INTO productos(descripcion, cantidad, precio_unitario) 
        VALUES(%s, %s, %s)
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(insertProductoSQL, (descripcion, cantidad, precio_unitario))
            # se confirma la insercion
            con.commit()

            return True

        # Si algo fallo entra aqui
        except con.Error as e:
            app.logger.info(e)

        # Siempre se va ejecutar
        finally:
            cur.close()
            con.close()

        return False

    def updateProducto(self, id, descripcion, cantidad, precio_unitario):

        updateProductoSQL = """
        UPDATE productos
        SET descripcion=%s, cantidad=%s, precio_unitario=%s
        WHERE id=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(updateProductoSQL, (descripcion, cantidad, precio_unitario, id))
            # se confirma la insercion
            con.commit()

            return True

        # Si algo fallo entra aqui
        except con.Error as e:
            app.logger.info(e)

        # Siempre se va ejecutar
        finally:
            cur.close()
            con.close()

        return False

    def deleteProducto(self, id):

        deleteProductoSQL = """
        DELETE FROM productos
        WHERE id=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(deleteProductoSQL, (id,))
            # se confirma la eliminacion
            con.commit()

            return True

        # Si algo fallo entra aqui
        except con.Error as e:
            app.logger.info(e)

        # Siempre se va ejecutar
        finally:
            cur.close()
            con.close()

        return False
