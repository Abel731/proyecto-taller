from app.conexion.Conexion import Conexion

class OrdenServicioDao:
    
    def __init__(self):
        self.conexion = Conexion()
    
    # ========================================================================
    # AGREGAR ORDEN DE SERVICIO
    # ========================================================================
    
    def agregar_orden(self, datos_orden, detalle_orden):
        """
        Registra una nueva orden de servicio (cabecera + detalle)
        
        Parámetros:
        - datos_orden: dict con id_presupuesto, id_cliente, id_empleado,
                       nro_orden_servicio, fecha_orden, fecha_inicio_estimada,
                       fecha_fin_estimada, observaciones
        - detalle_orden: list de dict con id_producto, cantidad, precio_unitario, id_impuesto
        
        Retorna:
        - id_orden_servicio si tiene éxito
        - None si hay error
        """
        con = None
        cursor = None
        
        try:
            print("========== DEBUG DAO: Iniciando agregar_orden ==========")
            print(f"DEBUG: datos_orden: {datos_orden}")
            print(f"DEBUG: detalle_orden (cantidad): {len(detalle_orden)}")
            
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            # 1. INSERTAR CABECERA
            print("DEBUG: Insertando cabecera de orden...")
            query_cabecera = """
            INSERT INTO orden_servicio 
            (id_presupuesto, id_cliente, id_empleado, nro_orden_servicio, 
             fecha_orden, fecha_inicio_estimada, fecha_fin_estimada, 
             observaciones, id_estado_orden)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)
            RETURNING id_orden_servicio
            """
            
            cursor.execute(query_cabecera, (
                datos_orden['id_presupuesto'],
                datos_orden['id_cliente'],
                datos_orden['id_empleado'],
                datos_orden['nro_orden_servicio'],
                datos_orden['fecha_orden'],
                datos_orden['fecha_inicio_estimada'],
                datos_orden['fecha_fin_estimada'],
                datos_orden.get('observaciones', None)
            ))
            
            id_orden_servicio = cursor.fetchone()[0]
            print(f"DEBUG: Orden insertada con ID: {id_orden_servicio}")
            
            # 2. INSERTAR DETALLE
            if not detalle_orden or len(detalle_orden) == 0:
                raise ValueError("La orden debe tener al menos un producto/servicio")
            
            print("DEBUG: Insertando detalle de orden...")
            query_detalle = """
            INSERT INTO orden_servicio_detalle 
            (id_orden_servicio, id_producto, cantidad, precio_unitario, id_impuesto)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            for idx, item in enumerate(detalle_orden, 1):
                print(f"DEBUG: Insertando producto {idx}/{len(detalle_orden)}: id={item['id_producto']}, cantidad={item['cantidad']}, precio={item['precio_unitario']}")
                cursor.execute(query_detalle, (
                    id_orden_servicio,
                    item['id_producto'],
                    item['cantidad'],
                    item['precio_unitario'],
                    item['id_impuesto']
                ))
            
            print(f"DEBUG: Insertados {len(detalle_orden)} productos en el detalle")
            
            con.commit()
            print(f"DEBUG: Transacción confirmada. ID Orden: {id_orden_servicio}")
            return id_orden_servicio
            
        except ValueError as ve:
            if con:
                con.rollback()
            print(f"❌ ERROR de validación: {str(ve)}")
            raise ve
            
        except Exception as e:
            if con:
                con.rollback()
            print(f"❌ ERROR en agregar_orden: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    # ========================================================================
    # OBTENER TODAS LAS ÓRDENES
    # ========================================================================
    
    def obtener_todas(self):
        """Retorna todas las órdenes de servicio con información resumida"""
        con = None
        cursor = None
        
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT * FROM vista_ordenes_servicio
            ORDER BY fecha_orden DESC
            """
            
            cursor.execute(query)
            ordenes = cursor.fetchall()
            
            lista_ordenes = []
            for ord in ordenes:
                lista_ordenes.append({
                    'id_orden_servicio': ord[0],
                    'nro_orden_servicio': ord[1],
                    'fecha_orden': ord[2].strftime('%Y-%m-%d') if ord[2] else None,
                    'fecha_inicio_estimada': ord[3].strftime('%Y-%m-%d') if ord[3] else None,
                    'fecha_fin_estimada': ord[4].strftime('%Y-%m-%d') if ord[4] else None,
                    'id_presupuesto': ord[5],
                    'nro_presupuesto': ord[6],
                    'id_cliente': ord[7],
                    'cliente': ord[8],
                    'cliente_ci': ord[9],
                    'cliente_ruc': ord[10],
                    'cliente_telefono': ord[11],
                    'empleado': ord[12],
                    'observaciones': ord[13],
                    'estado': ord[14],
                    'id_estado_orden': ord[15],
                    'cantidad_productos': ord[16],
                    'total_sin_iva': float(ord[17]) if ord[17] else 0,
                    'total_iva': float(ord[18]) if ord[18] else 0,
                    'total_general': float(ord[19]) if ord[19] else 0
                })
            
            return lista_ordenes
            
        except Exception as e:
            print(f"❌ ERROR en obtener_todas: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    # ========================================================================
    # OBTENER ORDEN POR ID
    # ========================================================================
    
    def obtener_por_id(self, id_orden_servicio):
        """Retorna una orden completa con su detalle y totales"""
        con = None
        cursor = None
        
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            # Obtener cabecera
            query_cabecera = """
            SELECT 
                os.id_orden_servicio,
                os.nro_orden_servicio,
                os.fecha_orden,
                os.fecha_inicio_estimada,
                os.fecha_fin_estimada,
                os.id_presupuesto,
                ps.nro_presupuesto,
                os.id_cliente,
                CONCAT(p.nombres, ' ', p.apellidos) AS cliente,
                p.ci AS cliente_ci,
                c.ruc AS cliente_ruc,
                c.telefono AS cliente_telefono,
                c.direccion AS cliente_direccion,
                os.id_empleado,
                CONCAT(emp_p.nombres, ' ', emp_p.apellidos) AS empleado,
                os.observaciones,
                os.id_estado_orden,
                e.descripcion AS estado
            FROM orden_servicio os
            INNER JOIN presupuesto_servicio ps ON os.id_presupuesto = ps.id_presupuesto
            INNER JOIN clientes c ON os.id_cliente = c.id_cliente
            INNER JOIN personas p ON c.id_cliente = p.id_persona
            INNER JOIN empleados emp ON os.id_empleado = emp.id_empleado
            INNER JOIN personas emp_p ON emp.id_empleado = emp_p.id_persona
            INNER JOIN estado_orden_servicio e ON os.id_estado_orden = e.id_estado_orden
            WHERE os.id_orden_servicio = %s
            """
            
            cursor.execute(query_cabecera, (id_orden_servicio,))
            cabecera = cursor.fetchone()
            
            if not cabecera:
                return None
            
            # Obtener detalle
            query_detalle = """
            SELECT 
                osd.id_producto,
                pr.nombre AS producto,
                osd.cantidad,
                osd.precio_unitario,
                osd.id_impuesto,
                imp.descripcion AS impuesto,
                imp.tasa AS tasa_iva
            FROM orden_servicio_detalle osd
            INNER JOIN productos pr ON osd.id_producto = pr.id_producto
            INNER JOIN impuestos imp ON osd.id_impuesto = imp.id_impuesto
            WHERE osd.id_orden_servicio = %s
            ORDER BY pr.nombre
            """
            
            cursor.execute(query_detalle, (id_orden_servicio,))
            detalle = cursor.fetchall()
            
            detalle_lista = []
            total_sin_iva = 0
            total_iva = 0
            total_general = 0
            
            for item in detalle:
                subtotal = item[2] * float(item[3])  # cantidad * precio_unitario
                iva = subtotal * (float(item[6]) / 100)  # subtotal * tasa_iva
                total = subtotal + iva
                
                total_sin_iva += subtotal
                total_iva += iva
                total_general += total
                
                detalle_lista.append({
                    'id_producto': item[0],
                    'producto': item[1],
                    'cantidad': item[2],
                    'precio_unitario': float(item[3]),
                    'id_impuesto': item[4],
                    'impuesto': item[5],
                    'tasa_iva': float(item[6]),
                    'subtotal': subtotal,
                    'iva': iva,
                    'total': total
                })
            
            return {
                'id_orden_servicio': cabecera[0],
                'nro_orden_servicio': cabecera[1],
                'fecha_orden': cabecera[2].strftime('%Y-%m-%d') if cabecera[2] else None,
                'fecha_inicio_estimada': cabecera[3].strftime('%Y-%m-%d') if cabecera[3] else None,
                'fecha_fin_estimada': cabecera[4].strftime('%Y-%m-%d') if cabecera[4] else None,
                'id_presupuesto': cabecera[5],
                'nro_presupuesto': cabecera[6],
                'id_cliente': cabecera[7],
                'cliente': cabecera[8],
                'cliente_ci': cabecera[9],
                'cliente_ruc': cabecera[10],
                'cliente_telefono': cabecera[11],
                'cliente_direccion': cabecera[12],
                'id_empleado': cabecera[13],
                'empleado': cabecera[14],
                'observaciones': cabecera[15],
                'id_estado_orden': cabecera[16],
                'estado': cabecera[17],
                'detalle': detalle_lista,
                'total_sin_iva': total_sin_iva,
                'total_iva': total_iva,
                'total_general': total_general
            }
            
        except Exception as e:
            print(f"❌ ERROR en obtener_por_id: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    # ========================================================================
    # CAMBIAR ESTADO DE ORDEN
    # ========================================================================
    
    def cambiar_estado(self, id_orden_servicio, id_estado_nuevo):
        """
        Cambia el estado de una orden
        
        Estados:
        1 = Borrador
        2 = Autorizada
        3 = Anulada
        """
        con = None
        cursor = None
        
        try:
            print(f"========== DEBUG DAO: Cambiando estado de orden {id_orden_servicio} ==========")
            
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            # Verificar que la orden existe
            query_check = """
            SELECT id_estado_orden 
            FROM orden_servicio 
            WHERE id_orden_servicio = %s
            """
            cursor.execute(query_check, (id_orden_servicio,))
            resultado = cursor.fetchone()
            
            if not resultado:
                raise ValueError(f"No se encontró la orden N° {id_orden_servicio}")
            
            estado_actual = resultado[0]
            print(f"DEBUG: Estado actual: {estado_actual}, Nuevo estado: {id_estado_nuevo}")
            
            # Validaciones de cambio de estado
            if estado_actual == 3:
                raise ValueError("No se puede modificar una orden anulada")
            
            if estado_actual == 2 and id_estado_nuevo != 3:
                raise ValueError("Una orden autorizada solo puede ser anulada")
            
            # Actualizar estado
            query_update = """
            UPDATE orden_servicio
            SET id_estado_orden = %s
            WHERE id_orden_servicio = %s
            """
            cursor.execute(query_update, (id_estado_nuevo, id_orden_servicio))
            
            con.commit()
            print(f"DEBUG: Estado actualizado exitosamente")
            return True
            
        except ValueError as ve:
            if con:
                con.rollback()
            print(f"❌ ERROR de validación: {str(ve)}")
            raise ve
            
        except Exception as e:
            if con:
                con.rollback()
            print(f"❌ ERROR en cambiar_estado: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    # ========================================================================
    # CONSULTAS AUXILIARES
    # ========================================================================
    
    def obtener_presupuestos_aprobados(self):
        """Retorna presupuestos en estado Aprobado (disponibles para generar orden)"""
        con = None
        cursor = None
        
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT 
                ps.id_presupuesto,
                ps.nro_presupuesto,
                ps.fecha_presupuesto,
                ps.fecha_validez,
                CONCAT(p.nombres, ' ', p.apellidos) AS cliente,
                ps.id_cliente
            FROM presupuesto_servicio ps
            INNER JOIN clientes c ON ps.id_cliente = c.id_cliente
            INNER JOIN personas p ON c.id_cliente = p.id_persona
            WHERE ps.id_estado_presupuesto = 2
            ORDER BY ps.fecha_presupuesto DESC
            """
            
            cursor.execute(query)
            presupuestos = cursor.fetchall()
            
            lista_presupuestos = []
            for pres in presupuestos:
                lista_presupuestos.append({
                    'id_presupuesto': pres[0],
                    'nro_presupuesto': pres[1],
                    'fecha_presupuesto': pres[2].strftime('%Y-%m-%d') if pres[2] else None,
                    'fecha_validez': pres[3].strftime('%Y-%m-%d') if pres[3] else None,
                    'cliente': pres[4],
                    'id_cliente': pres[5]
                })
            
            return lista_presupuestos
            
        except Exception as e:
            print(f"❌ ERROR en obtener_presupuestos_aprobados: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    def obtener_productos_presupuesto(self, id_presupuesto):
        """Retorna los productos de un presupuesto específico"""
        con = None
        cursor = None
        
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT 
                psd.id_producto,
                pr.nombre AS producto,
                psd.cantidad,
                psd.precio_unitario,
                psd.id_impuesto,
                imp.descripcion AS impuesto,
                imp.tasa AS tasa_iva
            FROM presupuesto_servicio_detalle psd
            INNER JOIN productos pr ON psd.id_producto = pr.id_producto
            INNER JOIN impuestos imp ON psd.id_impuesto = imp.id_impuesto
            WHERE psd.id_presupuesto = %s
            ORDER BY pr.nombre
            """
            
            cursor.execute(query, (id_presupuesto,))
            productos = cursor.fetchall()
            
            lista_productos = []
            for prod in productos:
                lista_productos.append({
                    'id_producto': prod[0],
                    'producto': prod[1],
                    'cantidad': prod[2],
                    'precio_unitario': float(prod[3]),
                    'id_impuesto': prod[4],
                    'impuesto': prod[5],
                    'tasa_iva': float(prod[6])
                })
            
            return lista_productos
            
        except Exception as e:
            print(f"❌ ERROR en obtener_productos_presupuesto: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()