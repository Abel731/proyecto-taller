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
            , pdp.id_proveedor
            , prov.ruc
            , prov.razon_social
            , pdp.id_pedido_compra
            , pdp.id_empleado
            , p.nombres
            , p.apellidos
            , pdp.id_sucursal
            , pdp.id_estpreprov
            , edp.descripcion AS estado
            , pdp.fecha_presupuesto
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
                    'id_proveedor': f'{presupuesto[1]} {presupuesto[2]}',
                    'id_pedido_compra': presupuesto[3],
                    'id_empleado': presupuesto[4],
                    'empleado': f'{presupuesto[5]} {presupuesto[6]}',
                    'id_sucursal': presupuesto[7],
                    'id_estpreprov': presupuesto[8],
                    'estado': presupuesto[9],
                    'fecha_presupuesto': presupuesto[10].strftime("%Y-%m-%d") if presupuesto[10] else None
                } for presupuesto in presupuestos]

        except Exception as e:
            app.logger.error(f"Error al obtener los presupuestos: {str(e)}")
        finally:
            cur.close()
            con.close()
        return []

    # Agregar presupuesto
    def agregar(self, presupuesto_dto: PresupuestoProvDto) -> bool:
        insertPresupuesto = """
        INSERT INTO public.presupuesto_prov
        (id_proveedor, id_pedido_compra, id_empleado, id_sucursal, id_estpreprov, fecha_presupuesto)
        VALUES(%s, %s, %s, %s, %s, %s)
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
            parametros = (presupuesto_dto.id_proveedor, presupuesto_dto.id_pedido_compra,
                         presupuesto_dto.id_empleado, presupuesto_dto.id_sucursal, 
                         presupuesto_dto.estado.id, presupuesto_dto.fecha_presupuesto)
            cur.execute(insertPresupuesto, parametros)
            id_presupuesto = cur.fetchone()[0]

            # Insertando los detalles del presupuesto
            if len(presupuesto_dto.detalle_presupuesto) > 0:
                for detalle in presupuesto_dto.detalle_presupuesto:
                    parametros_detalle = (id_presupuesto, detalle.id_producto, detalle.cantidad, detalle.precio_unitario)
                    cur.execute(insertDetallePresupuesto, parametros_detalle)

            # Confirmar transacción
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