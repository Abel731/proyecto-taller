from flask import current_app as app
from app.conexion.Conexion import Conexion
from app.dao.gestionar_compras.registrar_presupuesto_proveedor.dto.presupuesto_prov_dto \
    import PresupuestoProvDto

from datetime import datetime

class PresupuestoProvDao:

    # Obtener presupuestos
    def obtener_presupuestos(self):
        query_presupuestos = """
        SELECT
            pdp.id_presupuesto
            , pdp.id_pedido_compra
            , pdp.id_empleado
            , p.nombres
            , p.apellidos
            , pdp.id_sucursal
            , pdp.id_proveedor
            , prov.ruc
            , prov.razon_social
            , pdp.id_estpreprov
            , edp.descripcion AS estado
            , pdp.fecha_presupuesto
            , pdp.fecha_vencimiento
        FROM
            public.presupuesto_prov pdp
        LEFT JOIN proveedores prov
            ON prov.id_proveedor = pdp.id_proveedor
        LEFT JOIN empleados e
            ON e.id_empleado = pdp.id_empleado
        LEFT JOIN personas p
            ON p.id_persona = e.id_empleado
        LEFT JOIN estado_de_presupuesto_prov edp
            ON edp.id_estpreprov = pdp.id_estpreprov
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(query_presupuestos)
            presupuestos = cur.fetchall()
            return [{
                'id_presupuesto': presupuesto[0],
                'id_pedido_compra': presupuesto[1],
                'id_empleado': presupuesto[2],
                'empleado': f"{presupuesto[3]} {presupuesto[4]}",
                'id_sucursal': presupuesto[5],
                'id_proveedor': presupuesto[6],
                'proveedor': f"{presupuesto[7]} {presupuesto[8]}",
                'id_estpreprov': presupuesto[9],
                'estado': presupuesto[10],
                'fecha_presupuesto': (
                    presupuesto[11].strftime("%Y-%m-%d") if isinstance(presupuesto[11], datetime) else presupuesto[11]
                ),
                'fecha_vencimiento': (
                    presupuesto[12].strftime("%Y-%m-%d") if isinstance(presupuesto[12], datetime) else presupuesto[12]
                )
            } for presupuesto in presupuestos]

        except Exception as e:
            app.logger.error(f"Error al obtener los presupuestos: {str(e)}")
        finally:
            cur.close()
            con.close()
        return []

    def agregar(self, presupuesto_dto: PresupuestoProvDto) -> bool:
        insertPresupuesto = """
        INSERT INTO public.presupuesto_prov
        (id_proveedor, id_pedido_compra, id_empleado, id_sucursal, id_estpreprov, fecha_presupuesto, fecha_vencimiento)
        VALUES(%s, %s, %s, %s, %s, %s, %s)
        RETURNING id_presupuesto
        """

        insertDetallePresupuesto = """
        INSERT INTO public.presupuesto_prov_detalle
        (id_presupuesto, id_producto, cantidad, precio_unitario)
        VALUES(%s, %s, %s, %s)
        """

        conexion = Conexion()
        con = conexion.getConexion()
        con.autocommit = False
        cur = con.cursor()
        try:
            # Insertando el presupuesto
            parametros = (
                presupuesto_dto.id_proveedor, presupuesto_dto.id_pedido_compra,
                presupuesto_dto.id_empleado, presupuesto_dto.id_sucursal,
                presupuesto_dto.estado.id, presupuesto_dto.fecha_presupuesto,
                presupuesto_dto.fecha_vencimiento
            )
            cur.execute(insertPresupuesto, parametros)
            id_presupuesto = cur.fetchone()[0]

            # Insertando los detalles del presupuesto
            if len(presupuesto_dto.detalle_presupuesto) > 0:
                for detalle in presupuesto_dto.detalle_presupuesto:
                    parametros_detalle = (
                        id_presupuesto, detalle.id_producto, detalle.cantidad, detalle.precio_unitario
                    )
                    cur.execute(insertDetallePresupuesto, parametros_detalle)

            
            con.commit()
        except Exception as e:
            app.logger.error(f"Error al agregar el presupuesto: {str(e)}")
            con.rollback()
            return False
        finally:
            con.autocommit = True
            cur.close()
            con.close()
        return True


    # Anular presupuesto
    def anular(self, id_presupuesto: int) -> bool:
        updatePresupuesto = """
        UPDATE public.presupuesto_prov
        SET id_estpreprov = (SELECT id_estpreprov FROM estado_de_presupuesto_prov 
                             WHERE descripcion = 'Anulado')
        WHERE id_presupuesto = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            # Actualizar estado a 'Anulado'
            cur.execute(updatePresupuesto, (id_presupuesto,))
            con.commit()
        except Exception as e:
            app.logger.error(f"Error al anular el presupuesto: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
        return True