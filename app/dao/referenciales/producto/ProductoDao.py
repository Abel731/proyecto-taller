from flask import current_app as app
from app.conexion.Conexion import Conexion

class ProductoDao:

    def get_productos(self):

        producto_sql = """
        SELECT
            id_producto
            , nombre
            , precio_compra
        FROM
            public.productos
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(producto_sql)
            productos = cur.fetchall() # trae datos de la bd

            # Transformar los datos en una lista de diccionarios
            return [{'id_producto': item[0], 'nombre': item[1], 'precio_compra': item[2]} for item in productos]

        except Exception as e:
            app.logger.error(f"Error al obtener todos los productos: {str(e)}")
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

    def getProductoById(self, id_producto):

        productoSQL = """
        SELECT id_producto, nombre, precio_compra
        FROM productos WHERE id_producto=%s
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(productoSQL, (id_producto,))
            # trae datos de la bd
            productoEncontrado = cur.fetchone()
            # retorno los datos
            if productoEncontrado:
                return {
                    "id_producto": productoEncontrado[0],
                    "nombre": productoEncontrado[1],
                    "precio_compra": productoEncontrado[2]
                }
            return None
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

    def guardarProducto(self, nombre, precio_compra):

        insertProductoSQL = """
        INSERT INTO productos(nombre, precio_compra) 
        VALUES(%s, %s)
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(insertProductoSQL, (nombre, precio_compra))
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

    def updateProducto(self, id_producto, nombre, precio_compra):

        updateProductoSQL = """
        UPDATE productos
        SET nombre=%s, precio_compra=%s
        WHERE id_producto=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(updateProductoSQL, (nombre, precio_compra, id_producto))
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

    def deleteProducto(self, id_producto):

        deleteProductoSQL = """
        DELETE FROM productos
        WHERE id_producto=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(deleteProductoSQL, (id_producto,))
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