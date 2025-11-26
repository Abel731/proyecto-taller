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
            oc.id_sucursal,
            s.descripcion AS sucursal,
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
        LEFT JOIN sucursales s
            ON s.id_sucursal = oc.id_sucursal
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
                'id_sucursal': orden[8],
                'sucursal': orden[9],
                'id_proveedor': orden[10],
                'proveedor': orden[11]
            } for orden in ordenes]

        except Exception as e:
            app.logger.error(f"Error al obtener las ordenes: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def agregar(self, id_presupuesto, id_empleado, id_sucursal, id_estorden, fecha_orden, detalle_orden):
        insertOrdenCompraCabecera = """
        INSERT INTO public.orden_de_compra
        (id_presupuesto, id_empleado, id_sucursal, id_estorden, fecha_orden)
        VALUES(%s, %s, %s, %s, %s)
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
            # Insertando la cabecera con el estado seleccionado
            parametros = (id_presupuesto, id_empleado, id_sucursal, id_estorden, fecha_orden)
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

    def get_info_presupuesto(self, id_presupuesto):
        """
        Obtiene la información completa del presupuesto
        (sucursal, proveedor, empleado) para mostrar en el formulario
        """
        query = """
        SELECT
            pp.id_sucursal,
            s.descripcion AS sucursal,
            pp.id_proveedor,
            prov.razon_social AS proveedor,
            pp.id_empleado,
            CONCAT(p.nombres, ' ', p.apellidos) AS empleado
        FROM presupuesto_prov pp
        LEFT JOIN sucursales s ON s.id_sucursal = pp.id_sucursal
        LEFT JOIN proveedores prov ON prov.id_proveedor = pp.id_proveedor
        LEFT JOIN empleados e ON e.id_empleado = pp.id_empleado
        LEFT JOIN personas p ON p.id_persona = e.id_empleado
        WHERE pp.id_presupuesto = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(query, (id_presupuesto,))
            info = cur.fetchone()
            if info:
                return {
                    'id_sucursal': info[0],
                    'sucursal': info[1],
                    'id_proveedor': info[2],
                    'proveedor': info[3],
                    'id_empleado': info[4],
                    'empleado': info[5]
                }
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener info del presupuesto {id_presupuesto}: {e}")
            return None
        finally:
            cur.close()
            con.close()

    def get_orden_por_id(self, id_orden):
        """
        Obtiene una orden completa con:
        - Datos de la cabecera (presupuesto, empleado, sucursal, estado, fecha)
        - Detalle de productos (id, nombre, cantidad, precio)
        - Información del proveedor
        """
        query_cabecera = """
        SELECT
            oc.id_orden,
            oc.id_presupuesto,
            oc.id_empleado,
            CONCAT(p.nombres, ' ', p.apellidos) AS empleado,
            oc.id_sucursal,
            s.descripcion AS sucursal,
            oc.id_estorden,
            eoc.descripcion AS estado,
            oc.fecha_orden,
            pp.id_proveedor,
            prov.razon_social AS proveedor
        FROM
            public.orden_de_compra oc
        LEFT JOIN empleados e
            ON e.id_empleado = oc.id_empleado
        LEFT JOIN personas p
            ON p.id_persona = e.id_empleado
        LEFT JOIN sucursales s
            ON s.id_sucursal = oc.id_sucursal
        LEFT JOIN estado_orden_compra eoc
            ON eoc.id_estorden = oc.id_estorden
        LEFT JOIN presupuesto_prov pp
            ON pp.id_presupuesto = oc.id_presupuesto
        LEFT JOIN proveedores prov
            ON prov.id_proveedor = pp.id_proveedor
        WHERE oc.id_orden = %s
        """

        query_detalle = """
        SELECT
            ocd.id_producto,
            pro.nombre,
            ocd.cantidad,
            ocd.precio
        FROM orden_de_compra_detalle ocd
        LEFT JOIN productos pro ON pro.id_producto = ocd.id_producto
        WHERE ocd.id_orden = %s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            # Obtener cabecera
            cur.execute(query_cabecera, (id_orden,))
            cabecera = cur.fetchone()
            
            if not cabecera:
                
                return None

            # Obtener detalle
            cur.execute(query_detalle, (id_orden,))
            detalle = cur.fetchall()

            # Estructurar respuesta
            orden_completa = {
                'id_orden': cabecera[0],
                'id_presupuesto': cabecera[1],
                'id_empleado': cabecera[2],
                'empleado': cabecera[3],
                'id_sucursal': cabecera[4],
                'sucursal': cabecera[5],
                'id_estorden': cabecera[6],
                'estado': cabecera[7],
                'fecha_orden': (
                    cabecera[8].strftime("%Y-%m-%d") if isinstance(cabecera[8], datetime) else cabecera[8]
                ),
                'id_proveedor': cabecera[9],
                'proveedor': cabecera[10],
                'detalle': [
                    {
                        'id_producto': prod[0],
                        'nombre': prod[1],
                        'cantidad': prod[2],
                        'precio': float(prod[3]) if prod[3] else 0
                    }
                    for prod in detalle
                ]
            }

            return orden_completa

        except Exception as e:
                app.logger.error(f"Error al obtener orden {id_orden}: {str(e)}")
                return None
        finally:
            cur.close()
            con.close()

    def actualizar_estado(self, id_orden, id_estorden):
        """
            Actualiza el estado de una orden de compra
        """
        updateEstado = """
        UPDATE public.orden_de_compra
        SET id_estorden = %s
        WHERE id_orden = %s
        """
    
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(updateEstado, (id_estorden, id_orden))
            con.commit()
            
            if cur.rowcount > 0:
                return True
            return False
        
        except Exception as e:
            app.logger.error(f"Error al actualizar estado de orden {id_orden}: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()            

    def existe_orden_activa_para_presupuesto(self, id_presupuesto):
        """
        Verifica si ya existe una orden de compra activa para este presupuesto.
        Retorna True si existe una orden con estado diferente a Cancelada.
        """
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cur = con.cursor()
        
            query = """
            SELECT COUNT(*) 
            FROM orden_de_compra 
            WHERE id_presupuesto = %s 
            AND id_estorden != 4  -- 4 = Cancelada
            """
        
            cur.execute(query, (id_presupuesto,))
            resultado = cur.fetchone()
        
            return resultado[0] > 0  # True si existe al menos una orden activa
        
        except Exception as e:
            print(f"Error en existe_orden_activa_para_presupuesto: {str(e)}")
            return False
        finally:
            if conexion:
                cur.close()
                con.close()