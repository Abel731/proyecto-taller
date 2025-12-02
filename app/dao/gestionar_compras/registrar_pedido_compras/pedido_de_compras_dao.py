from flask import current_app as app
from app.conexion.Conexion import Conexion
from app.dao.gestionar_compras.registrar_pedido_compras.dto.pedido_de_compras_dto import PedidoDeComprasDto
from app.dao.gestionar_compras.registrar_pedido_compras.dto.pedido_de_compras_dto import PedidoDeComprasDto

class PedidoDeComprasDao:

    def obtener_pedidos(self):
        query_pedidos = """
        SELECT
            pdc.id_pedido_compra
            , pdc.id_empleado
            , p.nombres
            , p.apellidos
            , pdc.id_sucursal
            , pdc.id_epc
            , edpc.descripcion estado
            , pdc.fecha_pedido
            , pdc.id_deposito
        FROM
            public.pedido_de_compra pdc
        LEFT JOIN empleados e
            ON e.id_empleado = pdc.id_empleado
        LEFT JOIN personas p
            ON p.id_persona = e.id_empleado
        LEFT JOIN estado_de_pedido_compras edpc
        ON pdc.id_epc = edpc.id_epc
        """

        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(query_pedidos)
            pedidos = cur.fetchall()
            return [{
                    'id_pedido_compra': pedido[0]
                    , 'id_empleado': pedido[1]
                    , 'empleado': f'{pedido[2]} {pedido[3]}'
                    , 'id_sucursal': pedido[4]
                    , 'id_epc': pedido[5]
                    , 'estado': pedido[6]
                    , 'fecha_pedido': pedido[7].strftime("%Y-%m-%d") if pedido[7] else None
                    , 'id_deposito': pedido[8]
                } for pedido in pedidos]

        except Exception as e:
            app.logger.error(f"Error a obtener los pedidos: {str(e)}")
        finally:
            cur.close()
            con.close()
        return []

    # agregar
    def agregar(self, pedido_dto: PedidoDeComprasDto)->bool:
        insertPedidoCompraCabecera = """
        INSERT INTO public.pedido_de_compra
        (id_empleado, id_sucursal, id_epc, fecha_pedido, id_deposito)
        VALUES(%s, %s, %s, %s, %s)
        RETURNING id_pedido_compra
        """

        insertDetalleCompra = """
        INSERT INTO public.pedido_de_compra_detalle
        (id_pedido_compra, id_producto, cantidad)
        VALUES(%s, %s, %s)
        """

        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        con.autocommit = False
        cur = con.cursor()
        try:
            ## Insertando la cabecera
            # (id_empleado, id_sucursal, id_epc, fecha_pedido, id_deposito)
            parametros = (pedido_dto.id_empleado, pedido_dto.id_sucursal, \
                pedido_dto.estado.id, pedido_dto.fecha_pedido, pedido_dto.id_deposito,)
            cur.execute(insertPedidoCompraCabecera, parametros)
            id_pedido_compra = cur.fetchone()[0]

            ## Insertando el detalle del pedido
            if len(pedido_dto.detalle_pedido) > 0:
                for pedido in pedido_dto.detalle_pedido:
                    # (id_pedido_compra, id_producto, cantidad)
                    parametrosdetalle = (id_pedido_compra, pedido.id_producto, pedido.cantidad,)
                    cur.execute(insertDetalleCompra, parametrosdetalle)

            # Confirma la transacción
            con.commit()
        except Exception as e:
            app.logger.error(f"Error a agregar un nuevo pedido: {str(e)}")
            con.rollback()
            return False
        finally:
            con.autocommit = True
            cur.close()
            con.close()
        return True

    def obtener_pedidos_por_fecha(self):
        query = """
        SELECT 
            id_pedido_compra, 
            fecha_pedido 
        FROM pedido_de_compra
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(query)
            pedidos = cur.fetchall()
            return [
            {'id_pedido_compra': pedido[0], 'fecha_pedido': pedido[1]} 
            for pedido in pedidos
        ]
        except Exception as e:
            app.logger.error(f"Error al obtener pedidos: {e}")
            return []
        finally:
            cur.close()
            con.close()

    def get_productos_por_pedido(self, id_pedido):
        """
        Obtiene los productos de un pedido con el precio desde la tabla productos
        """
        con = None
        cur = None
        
        try:
            print(f"========== DEBUG DAO PEDIDO: Obteniendo productos del pedido {id_pedido} ==========")
            
            conexion = Conexion()
            con = conexion.getConexion()
            cur = con.cursor()
            
            # ✅ NOMBRE CORRECTO DE LA COLUMNA
            query = """
            SELECT 
                pcd.id_producto,
                pr.nombre AS producto,
                pcd.cantidad,
                pr.precio_compra AS precio_unitario
            FROM pedido_de_compra_detalle pcd
            INNER JOIN productos pr ON pcd.id_producto = pr.id_producto
            WHERE pcd.id_pedido_compra = %s
            """
            
            print(f"DEBUG DAO: Ejecutando query...")
            cur.execute(query, (id_pedido,))
            productos = cur.fetchall()
            
            print(f"DEBUG DAO: Productos encontrados: {len(productos) if productos else 0}")
            
            if not productos:
                return []
            
            detalle = []
            for prod in productos:
                producto_data = {
                    'id_producto': prod[0],
                    'nombre': prod[1],
                    'cantidad': prod[2],
                    'precio_unitario': float(prod[3]) if prod[3] else 0
                }
                print(f"DEBUG DAO: Producto: {producto_data}")
                detalle.append(producto_data)
            
            print(f"DEBUG DAO: Retornando {len(detalle)} productos")
            return detalle
            
        except Exception as e:
            print(f"❌ ERROR en get_productos_por_pedido: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
            
        finally:
            if cur:
                cur.close()
            if con:
                con.close()
            print("DEBUG DAO: Conexión cerrada")

    # modificar
    def modificar(self):
        pass

    # anular
    def anular(self):
        pass