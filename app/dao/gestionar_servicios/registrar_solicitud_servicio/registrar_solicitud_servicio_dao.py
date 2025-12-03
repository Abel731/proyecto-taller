from app.conexion.Conexion import Conexion

class SolicitudServicioDao:
    
    def __init__(self):
        self.conexion = Conexion()
    
    # ========================================================================
    # AGREGAR SOLICITUD DE SERVICIO
    # ========================================================================
    
    def agregar_solicitud(self, datos_solicitud, detalle_solicitud):
        """
        Registra una nueva solicitud de servicio (cabecera + detalle)
        
        Parámetros:
        - datos_solicitud: dict con id_cliente, id_tipo_servicio, id_empleado,
                           fecha_solicitud, hora_solicitud, descripcion_problema, observaciones
        - detalle_solicitud: list de dict con id_producto, cantidad, observacion
        
        Retorna:
        - id_solicitud si tiene éxito
        - None si hay error
        """
        con = None
        cursor = None
        
        try:
            print("========== DEBUG DAO: Iniciando agregar_solicitud ==========")
            print(f"DEBUG: datos_solicitud: {datos_solicitud}")
            print(f"DEBUG: detalle_solicitud (cantidad): {len(detalle_solicitud)}")
            
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            # 1. INSERTAR CABECERA
            print("DEBUG: Insertando cabecera de solicitud...")
            query_cabecera = """
            INSERT INTO solicitud_servicio 
            (id_cliente, id_tipo_servicio, id_empleado, fecha_solicitud, 
             hora_solicitud, descripcion_problema, observaciones, id_estado_solicitud)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
            RETURNING id_solicitud
            """
            
            cursor.execute(query_cabecera, (
                datos_solicitud['id_cliente'],
                datos_solicitud['id_tipo_servicio'],
                datos_solicitud['id_empleado'],
                datos_solicitud['fecha_solicitud'],
                datos_solicitud['hora_solicitud'],
                datos_solicitud['descripcion_problema'],
                datos_solicitud.get('observaciones', None)
            ))
            
            id_solicitud = cursor.fetchone()[0]
            print(f"DEBUG: Solicitud insertada con ID: {id_solicitud}")
            
            # 2. INSERTAR DETALLE (si hay productos)
            if detalle_solicitud and len(detalle_solicitud) > 0:
                print("DEBUG: Insertando detalle de solicitud...")
                query_detalle = """
                INSERT INTO solicitud_servicio_detalle 
                (id_solicitud, id_producto, cantidad, observacion)
                VALUES (%s, %s, %s, %s)
                """
                
                for idx, item in enumerate(detalle_solicitud, 1):
                    print(f"DEBUG: Insertando producto {idx}/{len(detalle_solicitud)}: id={item['id_producto']}, cantidad={item['cantidad']}")
                    cursor.execute(query_detalle, (
                        id_solicitud,
                        item['id_producto'],
                        item['cantidad'],
                        item.get('observacion', None)
                    ))
                
                print(f"DEBUG: Insertados {len(detalle_solicitud)} productos en el detalle")
            else:
                print("DEBUG: Solicitud sin productos (solo servicio)")
            
            con.commit()
            print(f"DEBUG: Transacción confirmada. ID Solicitud: {id_solicitud}")
            return id_solicitud
            
        except Exception as e:
            if con:
                con.rollback()
            print(f"❌ ERROR en agregar_solicitud: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    # ========================================================================
    # OBTENER TODAS LAS SOLICITUDES
    # ========================================================================
    
    def obtener_todas(self):
        """Retorna todas las solicitudes de servicio con información resumida"""
        con = None
        cursor = None
        
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT * FROM vista_solicitudes_servicio
            ORDER BY fecha_solicitud DESC, hora_solicitud DESC
            """
            
            cursor.execute(query)
            solicitudes = cursor.fetchall()
            
            lista_solicitudes = []
            for sol in solicitudes:
                lista_solicitudes.append({
                    'id_solicitud': sol[0],
                    'fecha_solicitud': sol[1].strftime('%Y-%m-%d') if sol[1] else None,
                    'hora_solicitud': sol[2].strftime('%H:%M:%S') if sol[2] else None,
                    'id_cliente': sol[3],
                    'cliente': sol[4],
                    'cliente_ci': sol[5],
                    'cliente_ruc': sol[6],
                    'cliente_telefono': sol[7],
                    'cliente_direccion': sol[8],
                    'tipo_servicio': sol[9],
                    'empleado': sol[10],
                    'descripcion_problema': sol[11],
                    'observaciones': sol[12],
                    'estado': sol[13],
                    'id_estado_solicitud': sol[14],
                    'cantidad_productos': sol[15]
                })
            
            return lista_solicitudes
            
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
    # OBTENER SOLICITUD POR ID
    # ========================================================================
    
    def obtener_por_id(self, id_solicitud):
        """Retorna una solicitud de servicio completa con su detalle"""
        con = None
        cursor = None
        
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            # Obtener cabecera
            query_cabecera = """
            SELECT 
                s.id_solicitud,
                s.fecha_solicitud,
                s.hora_solicitud,
                s.id_cliente,
                CONCAT(p.nombres, ' ', p.apellidos) AS cliente,
                p.ci AS cliente_ci,
                c.ruc AS cliente_ruc,
                c.telefono AS cliente_telefono,
                c.direccion AS cliente_direccion,
                s.id_tipo_servicio,
                ts.descripcion AS tipo_servicio,
                s.id_empleado,
                CONCAT(emp_p.nombres, ' ', emp_p.apellidos) AS empleado,
                s.descripcion_problema,
                s.observaciones,
                s.id_estado_solicitud,
                e.descripcion AS estado
            FROM solicitud_servicio s
            INNER JOIN clientes c ON s.id_cliente = c.id_cliente
            INNER JOIN personas p ON c.id_cliente = p.id_persona
            INNER JOIN tipo_servicio ts ON s.id_tipo_servicio = ts.id_tipo_servicio
            INNER JOIN empleados emp ON s.id_empleado = emp.id_empleado
            INNER JOIN personas emp_p ON emp.id_empleado = emp_p.id_persona
            INNER JOIN estado_solicitud e ON s.id_estado_solicitud = e.id_estado_solicitud
            WHERE s.id_solicitud = %s
            """
            
            cursor.execute(query_cabecera, (id_solicitud,))
            cabecera = cursor.fetchone()
            
            if not cabecera:
                return None
            
            # Obtener detalle
            query_detalle = """
            SELECT 
                sd.id_producto,
                pr.nombre AS producto,
                sd.cantidad,
                sd.observacion
            FROM solicitud_servicio_detalle sd
            INNER JOIN productos pr ON sd.id_producto = pr.id_producto
            WHERE sd.id_solicitud = %s
            ORDER BY pr.nombre
            """
            
            cursor.execute(query_detalle, (id_solicitud,))
            detalle = cursor.fetchall()
            
            detalle_lista = []
            for item in detalle:
                detalle_lista.append({
                    'id_producto': item[0],
                    'producto': item[1],
                    'cantidad': item[2],
                    'observacion': item[3]
                })
            
            return {
                'id_solicitud': cabecera[0],
                'fecha_solicitud': cabecera[1].strftime('%Y-%m-%d') if cabecera[1] else None,
                'hora_solicitud': cabecera[2].strftime('%H:%M:%S') if cabecera[2] else None,
                'id_cliente': cabecera[3],
                'cliente': cabecera[4],
                'cliente_ci': cabecera[5],
                'cliente_ruc': cabecera[6],
                'cliente_telefono': cabecera[7],
                'cliente_direccion': cabecera[8],
                'id_tipo_servicio': cabecera[9],
                'tipo_servicio': cabecera[10],
                'id_empleado': cabecera[11],
                'empleado': cabecera[12],
                'descripcion_problema': cabecera[13],
                'observaciones': cabecera[14],
                'id_estado_solicitud': cabecera[15],
                'estado': cabecera[16],
                'detalle': detalle_lista
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
    # CAMBIAR ESTADO DE SOLICITUD
    # ========================================================================
    
    def cambiar_estado(self, id_solicitud, id_estado_nuevo):
        """
        Cambia el estado de una solicitud
        
        Estados:
        1 = Pendiente
        2 = En Proceso
        3 = Finalizada
        4 = Anulada
        """
        con = None
        cursor = None
        
        try:
            print(f"========== DEBUG DAO: Cambiando estado de solicitud {id_solicitud} ==========")
            
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            # Verificar que la solicitud existe
            query_check = """
            SELECT id_estado_solicitud 
            FROM solicitud_servicio 
            WHERE id_solicitud = %s
            """
            cursor.execute(query_check, (id_solicitud,))
            resultado = cursor.fetchone()
            
            if not resultado:
                raise ValueError(f"No se encontró la solicitud N° {id_solicitud}")
            
            estado_actual = resultado[0]
            print(f"DEBUG: Estado actual: {estado_actual}, Nuevo estado: {id_estado_nuevo}")
            
            # Validaciones de cambio de estado
            if estado_actual == 4:
                raise ValueError("No se puede modificar una solicitud anulada")
            
            if estado_actual == 3 and id_estado_nuevo != 4:
                raise ValueError("Una solicitud finalizada solo puede ser anulada")
            
            # Actualizar estado
            query_update = """
            UPDATE solicitud_servicio
            SET id_estado_solicitud = %s
            WHERE id_solicitud = %s
            """
            cursor.execute(query_update, (id_estado_nuevo, id_solicitud))
            
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
    
    def obtener_clientes(self):
        """Retorna todos los clientes activos"""
        con = None
        cursor = None
        
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT 
                c.id_cliente,
                CONCAT(p.nombres, ' ', p.apellidos) AS cliente,
                p.ci,
                c.ruc,
                c.telefono,
                c.direccion
            FROM clientes c
            INNER JOIN personas p ON c.id_cliente = p.id_persona
            ORDER BY p.apellidos, p.nombres
            """
            
            cursor.execute(query)
            clientes = cursor.fetchall()
            
            lista_clientes = []
            for cli in clientes:
                lista_clientes.append({
                    'id_cliente': cli[0],
                    'cliente': cli[1],
                    'ci': cli[2],
                    'ruc': cli[3],
                    'telefono': cli[4],
                    'direccion': cli[5]
                })
            
            return lista_clientes
            
        except Exception as e:
            print(f"❌ ERROR en obtener_clientes: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    def obtener_tipos_servicio(self):
        """Retorna todos los tipos de servicio"""
        con = None
        cursor = None
        
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT id_tipo_servicio, descripcion
            FROM tipo_servicio
            ORDER BY descripcion
            """
            
            cursor.execute(query)
            tipos = cursor.fetchall()
            
            lista_tipos = []
            for tipo in tipos:
                lista_tipos.append({
                    'id_tipo_servicio': tipo[0],
                    'descripcion': tipo[1]
                })
            
            return lista_tipos
            
        except Exception as e:
            print(f"❌ ERROR en obtener_tipos_servicio: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    def obtener_productos(self):
        """Retorna todos los productos disponibles"""
        con = None
        cursor = None
        
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT id_producto, nombre, precio_compra
            FROM productos
            ORDER BY nombre
            """
            
            cursor.execute(query)
            productos = cursor.fetchall()
            
            lista_productos = []
            for prod in productos:
                lista_productos.append({
                    'id_producto': prod[0],
                    'nombre': prod[1],
                    'precio_compra': float(prod[2]) if prod[2] else 0
                })
            
            return lista_productos
            
        except Exception as e:
            print(f"❌ ERROR en obtener_productos: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()