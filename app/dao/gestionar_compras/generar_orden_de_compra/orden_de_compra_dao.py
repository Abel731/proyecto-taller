from flask import current_app as app
from app.conexion.Conexion import Conexion
from app.dao.gestionar_compras.generar_orden_de_compra.dto.orden_de_compra_dto import OrdenDeCompraDto
from datetime import datetime

class OrdenDeCompraDao:

    # Obtener órdenes de compra
    def obtener_ordenes(self):
        query_ordenes = """
        SELECT
            oc.id_orden,
            oc.id_proveedor,
            prov.ruc,
            prov.razon_social,
            oc.id_presupuesto,
            oc.id_empleado,
            p.nombres,
            p.apellidos,
            oc.id_sucursal,
            oc.id_estorden,
            eoc.descripcion AS estado,
            oc.fecha_orden
        FROM
            public.orden_de_compra oc
        LEFT JOIN proveedores prov
            ON prov.id_proveedor = oc.id_proveedor
        LEFT JOIN empleados e
            ON e.id_empleado = oc.id_empleado
        LEFT JOIN personas p
            ON p.id_persona = e.id_empleado
        LEFT JOIN sucursales suc
            ON suc.id_sucursal = oc.id_sucursal
        LEFT JOIN estado_orden_de_compra eoc
            ON eoc.id_estorden = oc.id_estorden
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(query_ordenes)
            ordenes = cur.fetchall()
            return [
                {
                    'id_orden': orden[0],
                    'id_proveedor': orden[1],
                    'proveedor': f"{orden[2]} {orden[3]}",
                    'id_presupuesto': orden[4],
                    'id_empleado': orden[5],
                    'empleado': f"{orden[6]} {orden[7]}",
                    'id_sucursal': orden[8],
                    'id_estorden': orden[9],
                    'estado': orden[10],
                    'fecha_orden': (
                        orden[11].strftime("%Y-%m-%d") if isinstance(orden[11], datetime) else orden[11]
                    )
                } for orden in ordenes
            ]

        except Exception as e:
            app.logger.error(f"Error al obtener las órdenes de compra: {str(e)}")
        finally:
            cur.close()
            con.close()
        return []
    
    def agregar(self, orden_dto: OrdenDeCompraDto) -> bool:
        insertOrden = """
        INSERT INTO public.orden_de_compra
        (id_proveedor, id_presupuesto, id_empleado, id_sucursal, id_estorden, fecha_orden)
        VALUES(%s, %s, %s, %s, %s, %s)
        RETURNING id_orden
        """

        insertDetalleOrden = """
        INSERT INTO public.orden_de_compra_detalle
        (id_orden, id_producto, cantidad, precio_unitario, total)
        VALUES(%s, %s, %s, %s, %s)
        """

        conexion = Conexion()
        con = conexion.getConexion()
        con.autocommit = False
        cur = con.cursor()
        try:
            # Insertando la orden de compra
            parametros_orden = (
                orden_dto.id_proveedor, orden_dto.id_presupuesto,
                orden_dto.id_empleado, orden_dto.id_sucursal,
                orden_dto.estado.id, orden_dto.fecha_orden
            )
            cur.execute(insertOrden, parametros_orden)
            id_orden = cur.fetchone()[0]

            # Insertando los detalles de la orden
            if len(orden_dto.detalle_orden) > 0:
                for detalle in orden_dto.detalle_orden:
                    parametros_detalle = (
                        id_orden, detalle.id_producto, detalle.cantidad,
                        detalle.precio_unitario, detalle.total
                    )
                    cur.execute(insertDetalleOrden, parametros_detalle)

            con.commit()
        except Exception as e:
            app.logger.error(f"Error al agregar la orden de compra: {str(e)}")
            con.rollback()
            return False
        finally:
            con.autocommit = True
            cur.close()
            con.close()
        return True