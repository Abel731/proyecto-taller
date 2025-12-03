from app.conexion.Conexion import Conexion

class DescuentoDao:
    
    def __init__(self):
        self.conexion = Conexion()
    
    # ========================================================================
    # AGREGAR DESCUENTO
    # ========================================================================
    
    def agregar_descuento(self, datos_descuento, detalle_descuento):
        """
        Registra un nuevo descuento (cabecera + detalle)
        
        Parámetros:
        - datos_descuento: dict con id_tipo_descuento, nombre_descuento,
                           descripcion, fecha_inicio, fecha_fin (puede ser None)
        - detalle_descuento: list de dict con id_producto, porcentaje_descuento
        
        Retorna:
        - id_descuento si tiene éxito
        - None si hay error
        """
        con = None
        cursor = None
        
        try:
            print("========== DEBUG DAO: Iniciando agregar_descuento ==========")
            print(f"DEBUG: datos_descuento: {datos_descuento}")
            print(f"DEBUG: detalle_descuento (cantidad): {len(detalle_descuento)}")
            
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            # 1. INSERTAR CABECERA
            print("DEBUG: Insertando cabecera de descuento...")
            query_cabecera = """
            INSERT INTO descuento 
            (id_tipo_descuento, nombre_descuento, descripcion, 
             fecha_inicio, fecha_fin, activo)
            VALUES (%s, %s, %s, %s, %s, TRUE)
            RETURNING id_descuento
            """
            
            cursor.execute(query_cabecera, (
                datos_descuento['id_tipo_descuento'],
                datos_descuento['nombre_descuento'],
                datos_descuento.get('descripcion', None),
                datos_descuento['fecha_inicio'],
                datos_descuento.get('fecha_fin', None)  # Puede ser NULL para descuentos permanentes
            ))
            
            id_descuento = cursor.fetchone()[0]
            print(f"DEBUG: Descuento insertado con ID: {id_descuento}")
            
            # 2. INSERTAR DETALLE
            if not detalle_descuento or len(detalle_descuento) == 0:
                raise ValueError("El descuento debe tener al menos un producto")
            
            print("DEBUG: Insertando detalle de descuento...")
            query_detalle = """
            INSERT INTO descuento_detalle 
            (id_descuento, id_producto, porcentaje_descuento)
            VALUES (%s, %s, %s)
            """
            
            for idx, item in enumerate(detalle_descuento, 1):
                print(f"DEBUG: Insertando producto {idx}/{len(detalle_descuento)}: id={item['id_producto']}, descuento={item['porcentaje_descuento']}%")
                cursor.execute(query_detalle, (
                    id_descuento,
                    item['id_producto'],
                    item['porcentaje_descuento']
                ))
            
            print(f"DEBUG: Insertados {len(detalle_descuento)} productos en el detalle")
            
            con.commit()
            print(f"DEBUG: Transacción confirmada. ID Descuento: {id_descuento}")
            return id_descuento
            
        except ValueError as ve:
            if con:
                con.rollback()
            print(f"❌ ERROR de validación: {str(ve)}")
            raise ve
            
        except Exception as e:
            if con:
                con.rollback()
            print(f"❌ ERROR en agregar_descuento: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    # ========================================================================
    # OBTENER TODOS LOS DESCUENTOS
    # ========================================================================
    
    def obtener_todos(self):
        """Retorna todos los descuentos con información resumida"""
        con = None
        cursor = None
        
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT * FROM vista_descuentos
            ORDER BY fecha_registro DESC
            """
            
            cursor.execute(query)
            descuentos = cursor.fetchall()
            
            lista_descuentos = []
            for desc in descuentos:
                lista_descuentos.append({
                    'id_descuento': desc[0],
                    'nombre_descuento': desc[1],
                    'descripcion': desc[2],
                    'fecha_inicio': desc[3].strftime('%Y-%m-%d') if desc[3] else None,
                    'fecha_fin': desc[4].strftime('%Y-%m-%d') if desc[4] else None,
                    'activo': desc[5],
                    'fecha_registro': desc[6].strftime('%Y-%m-%d %H:%M:%S') if desc[6] else None,
                    'id_tipo_descuento': desc[7],
                    'tipo_descuento': desc[8],
                    'cantidad_productos': desc[9],
                    'estado_vigencia': desc[10]
                })
            
            return lista_descuentos
            
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
    # OBTENER DESCUENTO POR ID
    # ========================================================================
    
    def obtener_por_id(self, id_descuento):
        """Retorna un descuento completo con su detalle"""
        con = None
        cursor = None
        
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            # Obtener cabecera
            query_cabecera = """
            SELECT 
                d.id_descuento,
                d.nombre_descuento,
                d.descripcion,
                d.fecha_inicio,
                d.fecha_fin,
                d.activo,
                d.fecha_registro,
                d.id_tipo_descuento,
                td.descripcion AS tipo_descuento,
                CASE 
                    WHEN d.activo = FALSE THEN 'Inactivo'
                    WHEN CURRENT_DATE < d.fecha_inicio THEN 'Próximo'
                    WHEN d.fecha_fin IS NULL THEN 'Permanente'
                    WHEN CURRENT_DATE > d.fecha_fin THEN 'Vencido'
                    ELSE 'Vigente'
                END AS estado_vigencia
            FROM descuento d
            INNER JOIN tipo_descuento td ON d.id_tipo_descuento = td.id_tipo_descuento
            WHERE d.id_descuento = %s
            """
            
            cursor.execute(query_cabecera, (id_descuento,))
            cabecera = cursor.fetchone()
            
            if not cabecera:
                return None
            
            # Obtener detalle
            query_detalle = """
            SELECT 
                dd.id_producto,
                pr.nombre AS producto,
                dd.porcentaje_descuento,
                pr.precio_compra
            FROM descuento_detalle dd
            INNER JOIN productos pr ON dd.id_producto = pr.id_producto
            WHERE dd.id_descuento = %s
            ORDER BY pr.nombre
            """
            
            cursor.execute(query_detalle, (id_descuento,))
            detalle = cursor.fetchall()
            
            detalle_lista = []
            for item in detalle:
                precio_original = float(item[3]) if item[3] else 0
                descuento_monto = precio_original * (float(item[2]) / 100)
                precio_final = precio_original - descuento_monto
                
                detalle_lista.append({
                    'id_producto': item[0],
                    'producto': item[1],
                    'porcentaje_descuento': float(item[2]),
                    'precio_original': precio_original,
                    'descuento': descuento_monto,
                    'precio_final': precio_final
                })
            
            return {
                'id_descuento': cabecera[0],
                'nombre_descuento': cabecera[1],
                'descripcion': cabecera[2],
                'fecha_inicio': cabecera[3].strftime('%Y-%m-%d') if cabecera[3] else None,
                'fecha_fin': cabecera[4].strftime('%Y-%m-%d') if cabecera[4] else None,
                'activo': cabecera[5],
                'fecha_registro': cabecera[6].strftime('%Y-%m-%d %H:%M:%S') if cabecera[6] else None,
                'id_tipo_descuento': cabecera[7],
                'tipo_descuento': cabecera[8],
                'estado_vigencia': cabecera[9],
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
    # ACTIVAR/DESACTIVAR DESCUENTO
    # ========================================================================
    
    def cambiar_estado(self, id_descuento, activo):
        """
        Activa o desactiva un descuento
        
        Parámetros:
        - id_descuento: ID del descuento
        - activo: True para activar, False para desactivar
        """
        con = None
        cursor = None
        
        try:
            print(f"========== DEBUG DAO: Cambiando estado de descuento {id_descuento} ==========")
            
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            # Verificar que el descuento existe
            query_check = """
            SELECT activo 
            FROM descuento 
            WHERE id_descuento = %s
            """
            cursor.execute(query_check, (id_descuento,))
            resultado = cursor.fetchone()
            
            if not resultado:
                raise ValueError(f"No se encontró el descuento N° {id_descuento}")
            
            estado_actual = resultado[0]
            print(f"DEBUG: Estado actual: {estado_actual}, Nuevo estado: {activo}")
            
            # Actualizar estado
            query_update = """
            UPDATE descuento
            SET activo = %s
            WHERE id_descuento = %s
            """
            cursor.execute(query_update, (activo, id_descuento))
            
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
    
    def obtener_tipos_descuento(self):
        """Retorna todos los tipos de descuento"""
        con = None
        cursor = None
        
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT id_tipo_descuento, descripcion
            FROM tipo_descuento
            ORDER BY descripcion
            """
            
            cursor.execute(query)
            tipos = cursor.fetchall()
            
            lista_tipos = []
            for tipo in tipos:
                lista_tipos.append({
                    'id_tipo_descuento': tipo[0],
                    'descripcion': tipo[1]
                })
            
            return lista_tipos
            
        except Exception as e:
            print(f"❌ ERROR en obtener_tipos_descuento: {str(e)}")
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