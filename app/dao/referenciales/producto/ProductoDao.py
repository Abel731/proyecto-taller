from flask import current_app as app
from app.conexion.Conexion import Conexion

class ProductoDao:

    def getProductos(self):

        productoSQL = """
        SELECT id, descripcion, cantidad, precio_unitario
        FROM productos
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(productoSQL)
            # trae datos de la bd
            lista_productos = cur.fetchall()
            # retorno los datos
            lista_ordenada = []
            for item in lista_productos:
                lista_ordenada.append({
                    "id": item[0],
                    "descripcion": item[1],
                    "cantidad": item[2],
                    "precio_unitario": item[3]
                })
            return lista_ordenada
        except con.Error as e:
            app.logger.info(e)
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
