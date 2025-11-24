from flask import current_app as app
from app.conexion.Conexion import Conexion
from datetime import datetime

class OrdenCompraDao:

    def obtener_ordenes(self):
        query_ordenes = """
        SELECT
            oc.id_orden,
            oc.id_presupuesto,
            oc.id_empleado,
            p.nombres,
            p.apellidos,
            oc.id_estorden,
            eoc.descripcion AS estado,
            oc.fecha_orden,
            pp.id_proveedor,
            prov.razon_social
        FROM
            public.orden_de_compra oc
        LEFT JOIN empleados e
            ON e.id_empleado = oc.id_empleado
        LEFT JOIN personas p
            ON p.id_persona = e.id_empleado
        LEFT JOIN estado_orden_compra eoc
            ON eoc.id_estorden = oc.id_estorden
        LEFT JOIN presupuesto_prov pp
            ON pp.id_presupuesto = oc.id_presupuesto
        LEFT JOIN proveedores prov
            ON prov.id_proveedor = pp.id_proveedor
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(query_ordenes)
            ordenes = cur.fetchall()
            return [{
                'id_orden': orden[0],
                'id_presupuesto': orden[1],
                'id_empleado': orden[2],
                'empleado': f'{orden[3]} {orden[4]}',
                'id_estorden': orden[5],
                'estado': orden[6],
                'fecha_orden': (
                    orden[7].strftime("%Y-%m-%d") if isinstance(orden[7], datetime) else orden[7]
                ),
                'id_proveedor': orden[8],
                'proveedor': orden[9]
            } for orden in ordenes]

        except Exception as e:
            app.logger.error(f"Error al obtener las ordenes: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def agregar(self, id_presupuesto, id_empleado, fecha_orden, detalle_orden):
        insertOrdenCompraCabecera = """
        INSERT INTO public.orden_de_compra
        (id_presupuesto, id_empleado, id_estorden, fecha_orden)
        VALUES(%s, %s, %s, %s)
        RETURNING id_orden
        """

        insertDetalleOrden = """
        INSERT INTO public.orden_de_compra_detalle
        (id_orden, id_producto, cantidad, precio)
        VALUES(%s, %s, %s, %s)
        """

        conexion = Conexion()
        con = conexion.getConexion()
        con.autocommit = False
        cur = con.cursor()
        try:
            # Insertando la cabecera (estado por defecto: 1 = Pendiente)
            parametros = (id_presupuesto, id_empleado, 1, fecha_orden)
            cur.execute(insertOrdenCompraCabecera, parametros)
            id_orden = cur.fetchone()[0]

            # Insertando el detalle de la orden
            if len(detalle_orden) > 0:
                for detalle in detalle_orden:
                    parametros_detalle = (
                        id_orden,
                        detalle['id_producto'],
                        detalle['cantidad'],
                        detalle['precio']
                    )
                    cur.execute(insertDetalleOrden, parametros_detalle)

            # Confirma la transacción
            con.commit()
            return True
        except Exception as e:
            app.logger.error(f"Error al agregar una nueva orden: {str(e)}")
            con.rollback()
            return False
        finally:
            con.autocommit = True
            cur.close()
            con.close()

    def anular(self, id_orden):
        updateOrden = """
        UPDATE public.orden_de_compra
        SET id_estorden = (SELECT id_estorden FROM estado_orden_compra 
                           WHERE descripcion = 'Cancelada')
        WHERE id_orden = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(updateOrden, (id_orden,))
            con.commit()
            return True
        except Exception as e:
            app.logger.error(f"Error al anular la orden: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def get_detalle_presupuesto(self, id_presupuesto):
        """
        Obtiene los productos del presupuesto seleccionado
        para cargarlos en el formulario de orden de compra
        """
        query = """
        SELECT
            ppd.id_producto,
            pro.nombre,
            ppd.cantidad,
            ppd.precio_unitario
        FROM presupuesto_prov_detalle ppd
        LEFT JOIN productos pro ON ppd.id_producto = pro.id_producto
        WHERE ppd.id_presupuesto = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(query, (id_presupuesto,))
            productos = cur.fetchall()
            return [
                {
                    'id_producto': producto[0],
                    'nombre': producto[1],
                    'cantidad': producto[2],
                    'precio': producto[3]
                }
                for producto in productos
            ]
        except Exception as e:
            app.logger.error(f"Error al obtener detalle del presupuesto {id_presupuesto}: {e}")
            return []
        finally:
            cur.close()
            con.close()