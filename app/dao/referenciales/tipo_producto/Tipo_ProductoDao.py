from flask import current_app as app
from app.conexion.Conexion import Conexion

class Tipo_ProductoDao:

    def getTipoProductos(self):
        tipo_productoSQL = """
        SELECT id, descripcion
        FROM tipo_producto
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(tipo_productoSQL)
            lista_tipo_productos = cur.fetchall()
            lista_ordenada = []
            for item in lista_tipo_productos:
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

    def getTipoProductoById(self, id):
        tipo_productoSQL = """
        SELECT id, descripcion
        FROM tipo_producto WHERE id=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(tipo_productoSQL, (id,))
            tipo_productoEncontrado = cur.fetchone()
            return {
                "id": tipo_productoEncontrado[0],
                "descripcion": tipo_productoEncontrado[1]
            }
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

    def guardarTipoProducto(self, descripcion):
        insertTipoProductoSQL = """
        INSERT INTO tipo_producto(descripcion) VALUES(%s)
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(insertTipoProductoSQL, (descripcion,))
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False

    def updateTipoProducto(self, id, descripcion):
        updateTipoProductoSQL = """
        UPDATE tipo_producto
        SET descripcion=%s
        WHERE id=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(updateTipoProductoSQL, (descripcion, id,))
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False

    def deleteTipoProducto(self, id):
        deleteTipoProductoSQL = """
        DELETE FROM tipo_producto
        WHERE id=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(deleteTipoProductoSQL, (id,))
            con.commit()
            return True
        except con.Error as e:
            app.logger.info(e)
        finally:
            cur.close()
            con.close()

        return False
