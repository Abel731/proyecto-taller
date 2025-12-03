from app.conexion.Conexion import Conexion

class PresupuestoServicioDao:
    
    def __init__(self):
        self.conexion = Conexion()
    
    # ========================================================================
    # AGREGAR PRESUPUESTO DE SERVICIO
    # ========================================================================
    
    def agregar_presupuesto(self, datos_presupuesto, detalle_presupuesto):
        """
        Registra un nuevo presupuesto de servicio (cabecera + detalle)
        
        Parámetros:
        - datos_presupuesto: dict con id_solicitud, id_cliente, id_empleado,
                             nro_presupuesto, fecha_presupuesto, fecha_validez, observaciones
        - detalle_presupuesto: list de dict con id_producto, cantidad, precio_unitario, id_impuesto
        
        Retorna:
        - id_presupuesto si tiene éxito
        - None si hay error
        """
        con = None
        cursor = None
        
        try:
            print("========== DEBUG DAO: Iniciando agregar_presupuesto ==========")
            print(f"DEBUG: datos_presupuesto: {datos_presupuesto}")
            print(f"DEBUG: detalle_presupuesto (cantidad): {len(detalle_presupuesto)}")
            
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            # 1. INSERTAR CABECERA
            print("DEBUG: Insertando cabecera de presupuesto...")
            query_cabecera = """
            INSERT INTO presupuesto_servicio 
            (id_solicitud, id_cliente, id_empleado, nro_presupuesto, 
             fecha_presupuesto, fecha_validez, observaciones, id_estado_presupuesto)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
            RETURNING id_presupuesto
            """
            
            cursor.execute(query_cabecera, (
                datos_presupuesto['id_solicitud'],
                datos_presupuesto['id_cliente'],
                datos_presupuesto['id_empleado'],
                datos_presupuesto['nro_presupuesto'],
                datos_presupuesto['fecha_presupuesto'],
                datos_presupuesto['fecha_validez'],
                datos_presupuesto.get('observaciones', None)
            ))
            
            id_presupuesto = cursor.fetchone()[0]
            print(f"DEBUG: Presupuesto insertado con ID: {id_presupuesto}")
            
            # 2. INSERTAR DETALLE
            if not detalle_presupuesto or len(detalle_presupuesto) == 0:
                raise ValueError("El presupuesto debe tener al menos un producto/servicio")
            
            print("DEBUG: Insertando detalle de presupuesto...")
            query_detalle = """
            INSERT INTO presupuesto_servicio_detalle 
            (id_presupuesto, id_producto, cantidad, precio_unitario, id_impuesto)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            for idx, item in enumerate(detalle_presupuesto, 1):
                print(f"DEBUG: Insertando producto {idx}/{len(detalle_presupuesto)}: id={item['id_producto']}, cantidad={item['cantidad']}, precio={item['precio_unitario']}")
                cursor.execute(query_detalle, (
                    id_presupuesto,
                    item['id_producto'],
                    item['cantidad'],
                    item['precio_unitario'],
                    item['id_impuesto']
                ))
            
            print(f"DEBUG: Insertados {len(detalle_presupuesto)} productos en el detalle")
            
            con.commit()
            print(f"DEBUG: Transacción confirmada. ID Presupuesto: {id_presupuesto}")
            return id_presupuesto
            
        except ValueError as ve:
            if con:
                con.rollback()
            print(f"❌ ERROR de validación: {str(ve)}")
            raise ve
            
        except Exception as e:
            if con:
                con.rollback()
            print(f"❌ ERROR en agregar_presupuesto: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    # ========================================================================
    # OBTENER TODOS LOS PRESUPUESTOS
    # ========================================================================
    
    def obtener_todos(self):
        """Retorna todos los presupuestos de servicio con información resumida"""
        con = None
        cursor = None
        
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT * FROM vista_presupuestos_servicio
            ORDER BY fecha_presupuesto DESC
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
                    'id_solicitud': pres[4],
                    'nro_solicitud': pres[5],
                    'id_cliente': pres[6],
                    'cliente': pres[7],
                    'cliente_ci': pres[8],
                    'cliente_ruc': pres[9],
                    'cliente_telefono': pres[10],
                    'empleado': pres[11],
                    'observaciones': pres[12],
                    'estado': pres[13],
                    'id_estado_presupuesto': pres[14],
                    'cantidad_productos': pres[15],
                    'total_sin_iva': float(pres[16]) if pres[16] else 0,
                    'total_iva': float(pres[17]) if pres[17] else 0,
                    'total_general': float(pres[18]) if pres[18] else 0
                })
            
            return lista_presupuestos
            
        except Exception as e:
            print(f"❌ ERROR en obtener_todos: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    # ========================================================================
    # OBTENER PRESUPUESTO POR ID
    # ========================================================================
    
    def obtener_por_id(self, id_presupuesto):
        """Retorna un presupuesto completo con su detalle y totales"""
        con = None
        cursor = None
        
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            # Obtener cabecera
            query_cabecera = """
            SELECT 
                ps.id_presupuesto,
                ps.nro_presupuesto,
                ps.fecha_presupuesto,
                ps.fecha_validez,
                ps.id_solicitud,
                CONCAT('SOL-', LPAD(ps.id_solicitud::TEXT, 6, '0')) AS nro_solicitud,
                ps.id_cliente,
                CONCAT(p.nombres, ' ', p.apellidos) AS cliente,
                p.ci AS cliente_ci,
                c.ruc AS cliente_ruc,
                c.telefono AS cliente_telefono,
                c.direccion AS cliente_direccion,
                ps.id_empleado,
                CONCAT(emp_p.nombres, ' ', emp_p.apellidos) AS empleado,
                ps.observaciones,
                ps.id_estado_presupuesto,
                e.descripcion AS estado
            FROM presupuesto_servicio ps
            INNER JOIN clientes c ON ps.id_cliente = c.id_cliente
            INNER JOIN personas p ON c.id_cliente = p.id_persona
            INNER JOIN empleados emp ON ps.id_empleado = emp.id_empleado
            INNER JOIN personas emp_p ON emp.id_empleado = emp_p.id_persona
            INNER JOIN estado_presupuesto_servicio e ON ps.id_estado_presupuesto = e.id_estado_presupuesto
            WHERE ps.id_presupuesto = %s
            """
            
            cursor.execute(query_cabecera, (id_presupuesto,))
            cabecera = cursor.fetchone()
            
            if not cabecera:
                return None
            
            # Obtener detalle
            query_detalle = """
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
            
            cursor.execute(query_detalle, (id_presupuesto,))
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
                'id_presupuesto': cabecera[0],
                'nro_presupuesto': cabecera[1],
                'fecha_presupuesto': cabecera[2].strftime('%Y-%m-%d') if cabecera[2] else None,
                'fecha_validez': cabecera[3].strftime('%Y-%m-%d') if cabecera[3] else None,
                'id_solicitud': cabecera[4],
                'nro_solicitud': cabecera[5],
                'id_cliente': cabecera[6],
                'cliente': cabecera[7],
                'cliente_ci': cabecera[8],
                'cliente_ruc': cabecera[9],
                'cliente_telefono': cabecera[10],
                'cliente_direccion': cabecera[11],
                'id_empleado': cabecera[12],
                'empleado': cabecera[13],
                'observaciones': cabecera[14],
                'id_estado_presupuesto': cabecera[15],
                'estado': cabecera[16],
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
    # CAMBIAR ESTADO DE PRESUPUESTO
    # ========================================================================
    
    def cambiar_estado(self, id_presupuesto, id_estado_nuevo):
        """
        Cambia el estado de un presupuesto
        
        Estados:
        1 = Pendiente
        2 = Aprobado
        3 = Rechazado
        4 = Anulado
        """
        con = None
        cursor = None
        
        try:
            print(f"========== DEBUG DAO: Cambiando estado de presupuesto {id_presupuesto} ==========")
            
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            # Verificar que el presupuesto existe
            query_check = """
            SELECT id_estado_presupuesto 
            FROM presupuesto_servicio 
            WHERE id_presupuesto = %s
            """
            cursor.execute(query_check, (id_presupuesto,))
            resultado = cursor.fetchone()
            
            if not resultado:
                raise ValueError(f"No se encontró el presupuesto N° {id_presupuesto}")
            
            estado_actual = resultado[0]
            print(f"DEBUG: Estado actual: {estado_actual}, Nuevo estado: {id_estado_nuevo}")
            
            # Validaciones de cambio de estado
            if estado_actual == 4:
                raise ValueError("No se puede modificar un presupuesto anulado")
            
            if estado_actual in [2, 3]:  # Aprobado o Rechazado
                if id_estado_nuevo != 4:
                    raise ValueError("Un presupuesto aprobado/rechazado solo puede ser anulado")
            
            # Actualizar estado
            query_update = """
            UPDATE presupuesto_servicio
            SET id_estado_presupuesto = %s
            WHERE id_presupuesto = %s
            """
            cursor.execute(query_update, (id_estado_nuevo, id_presupuesto))
            
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
    
    def obtener_solicitudes_finalizadas(self):
        """Retorna solicitudes en estado Finalizada (disponibles para presupuestar)"""
        con = None
        cursor = None
        
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT 
                s.id_solicitud,
                CONCAT('SOL-', LPAD(s.id_solicitud::TEXT, 6, '0')) AS nro_solicitud,
                s.fecha_solicitud,
                CONCAT(p.nombres, ' ', p.apellidos) AS cliente,
                ts.descripcion AS tipo_servicio,
                s.id_cliente,
                s.id_tipo_servicio
            FROM solicitud_servicio s
            INNER JOIN clientes c ON s.id_cliente = c.id_cliente
            INNER JOIN personas p ON c.id_cliente = p.id_persona
            INNER JOIN tipo_servicio ts ON s.id_tipo_servicio = ts.id_tipo_servicio
            WHERE s.id_estado_solicitud = 3
            ORDER BY s.fecha_solicitud DESC
            """
            
            cursor.execute(query)
            solicitudes = cursor.fetchall()
            
            lista_solicitudes = []
            for sol in solicitudes:
                lista_solicitudes.append({
                    'id_solicitud': sol[0],
                    'nro_solicitud': sol[1],
                    'fecha_solicitud': sol[2].strftime('%Y-%m-%d') if sol[2] else None,
                    'cliente': sol[3],
                    'tipo_servicio': sol[4],
                    'id_cliente': sol[5],
                    'id_tipo_servicio': sol[6]
                })
            
            return lista_solicitudes
            
        except Exception as e:
            print(f"❌ ERROR en obtener_solicitudes_finalizadas: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    def obtener_productos_solicitud(self, id_solicitud):
        """Retorna los productos de una solicitud específica"""
        con = None
        cursor = None
        
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT 
                sd.id_producto,
                pr.nombre AS producto,
                sd.cantidad,
                pr.precio_compra,
                sd.observacion
            FROM solicitud_servicio_detalle sd
            INNER JOIN productos pr ON sd.id_producto = pr.id_producto
            WHERE sd.id_solicitud = %s
            ORDER BY pr.nombre
            """
            
            cursor.execute(query, (id_solicitud,))
            productos = cursor.fetchall()
            
            lista_productos = []
            for prod in productos:
                lista_productos.append({
                    'id_producto': prod[0],
                    'producto': prod[1],
                    'cantidad': prod[2],
                    'precio_compra': float(prod[3]) if prod[3] else 0,
                    'observacion': prod[4]
                })
            
            return lista_productos
            
        except Exception as e:
            print(f"❌ ERROR en obtener_productos_solicitud: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    def obtener_impuestos(self):
        """Retorna todos los impuestos disponibles"""
        con = None
        cursor = None
        
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT id_impuesto, descripcion, tasa
            FROM impuestos
            ORDER BY tasa
            """
            
            cursor.execute(query)
            impuestos = cursor.fetchall()
            
            lista_impuestos = []
            for imp in impuestos:
                lista_impuestos.append({
                    'id_impuesto': imp[0],
                    'descripcion': imp[1],
                    'tasa': float(imp[2])
                })
            
            return lista_impuestos
            
        except Exception as e:
            print(f"❌ ERROR en obtener_impuestos: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()