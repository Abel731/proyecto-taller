from app.conexion.Conexion import Conexion

class PromocionDao:
    
    def __init__(self):
        self.conexion = Conexion()
    
    # ========================================================================
    # AGREGAR PROMOCIÓN
    # ========================================================================
    
    def agregar_promocion(self, datos_promocion, detalle_promocion):
        """
        Registra una nueva promoción (cabecera + detalle)
        
        Parámetros:
        - datos_promocion: dict con id_tipo_promocion, nombre_promocion,
                           descripcion, fecha_inicio, fecha_fin
        - detalle_promocion: list de dict con id_producto, porcentaje_descuento
        
        Retorna:
        - id_promocion si tiene éxito
        - None si hay error
        """
        con = None
        cursor = None
        
        try:
            print("========== DEBUG DAO: Iniciando agregar_promocion ==========")
            print(f"DEBUG: datos_promocion: {datos_promocion}")
            print(f"DEBUG: detalle_promocion (cantidad): {len(detalle_promocion)}")
            
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            # 1. INSERTAR CABECERA
            print("DEBUG: Insertando cabecera de promoción...")
            query_cabecera = """
            INSERT INTO promocion 
            (id_tipo_promocion, nombre_promocion, descripcion, 
             fecha_inicio, fecha_fin, activa)
            VALUES (%s, %s, %s, %s, %s, TRUE)
            RETURNING id_promocion
            """
            
            cursor.execute(query_cabecera, (
                datos_promocion['id_tipo_promocion'],
                datos_promocion['nombre_promocion'],
                datos_promocion.get('descripcion', None),
                datos_promocion['fecha_inicio'],
                datos_promocion['fecha_fin']
            ))
            
            id_promocion = cursor.fetchone()[0]
            print(f"DEBUG: Promoción insertada con ID: {id_promocion}")
            
            # 2. INSERTAR DETALLE
            if not detalle_promocion or len(detalle_promocion) == 0:
                raise ValueError("La promoción debe tener al menos un producto")
            
            print("DEBUG: Insertando detalle de promoción...")
            query_detalle = """
            INSERT INTO promocion_detalle 
            (id_promocion, id_producto, porcentaje_descuento)
            VALUES (%s, %s, %s)
            """
            
            for idx, item in enumerate(detalle_promocion, 1):
                print(f"DEBUG: Insertando producto {idx}/{len(detalle_promocion)}: id={item['id_producto']}, descuento={item['porcentaje_descuento']}%")
                cursor.execute(query_detalle, (
                    id_promocion,
                    item['id_producto'],
                    item['porcentaje_descuento']
                ))
            
            print(f"DEBUG: Insertados {len(detalle_promocion)} productos en el detalle")
            
            con.commit()
            print(f"DEBUG: Transacción confirmada. ID Promoción: {id_promocion}")
            return id_promocion
            
        except ValueError as ve:
            if con:
                con.rollback()
            print(f"❌ ERROR de validación: {str(ve)}")
            raise ve
            
        except Exception as e:
            if con:
                con.rollback()
            print(f"❌ ERROR en agregar_promocion: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    # ========================================================================
    # OBTENER TODAS LAS PROMOCIONES
    # ========================================================================
    
    def obtener_todas(self):
        """Retorna todas las promociones con información resumida"""
        con = None
        cursor = None
        
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT * FROM vista_promociones
            ORDER BY fecha_registro DESC
            """
            
            cursor.execute(query)
            promociones = cursor.fetchall()
            
            lista_promociones = []
            for prom in promociones:
                lista_promociones.append({
                    'id_promocion': prom[0],
                    'nombre_promocion': prom[1],
                    'descripcion': prom[2],
                    'fecha_inicio': prom[3].strftime('%Y-%m-%d') if prom[3] else None,
                    'fecha_fin': prom[4].strftime('%Y-%m-%d') if prom[4] else None,
                    'activa': prom[5],
                    'fecha_registro': prom[6].strftime('%Y-%m-%d %H:%M:%S') if prom[6] else None,
                    'id_tipo_promocion': prom[7],
                    'tipo_promocion': prom[8],
                    'cantidad_productos': prom[9],
                    'estado_vigencia': prom[10]
                })
            
            return lista_promociones
            
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
    # OBTENER PROMOCIÓN POR ID
    # ========================================================================
    
    def obtener_por_id(self, id_promocion):
        """Retorna una promoción completa con su detalle"""
        con = None
        cursor = None
        
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            # Obtener cabecera
            query_cabecera = """
            SELECT 
                p.id_promocion,
                p.nombre_promocion,
                p.descripcion,
                p.fecha_inicio,
                p.fecha_fin,
                p.activa,
                p.fecha_registro,
                p.id_tipo_promocion,
                tp.descripcion AS tipo_promocion,
                CASE 
                    WHEN p.activa = FALSE THEN 'Inactiva'
                    WHEN CURRENT_DATE < p.fecha_inicio THEN 'Próxima'
                    WHEN CURRENT_DATE > p.fecha_fin THEN 'Vencida'
                    ELSE 'Vigente'
                END AS estado_vigencia
            FROM promocion p
            INNER JOIN tipo_promocion tp ON p.id_tipo_promocion = tp.id_tipo_promocion
            WHERE p.id_promocion = %s
            """
            
            cursor.execute(query_cabecera, (id_promocion,))
            cabecera = cursor.fetchone()
            
            if not cabecera:
                return None
            
            # Obtener detalle
            query_detalle = """
            SELECT 
                pd.id_producto,
                pr.nombre AS producto,
                pd.porcentaje_descuento,
                pr.precio_compra
            FROM promocion_detalle pd
            INNER JOIN productos pr ON pd.id_producto = pr.id_producto
            WHERE pd.id_promocion = %s
            ORDER BY pr.nombre
            """
            
            cursor.execute(query_detalle, (id_promocion,))
            detalle = cursor.fetchall()
            
            detalle_lista = []
            for item in detalle:
                precio_original = float(item[3]) if item[3] else 0
                descuento = precio_original * (float(item[2]) / 100)
                precio_final = precio_original - descuento
                
                detalle_lista.append({
                    'id_producto': item[0],
                    'producto': item[1],
                    'porcentaje_descuento': float(item[2]),
                    'precio_original': precio_original,
                    'descuento': descuento,
                    'precio_final': precio_final
                })
            
            return {
                'id_promocion': cabecera[0],
                'nombre_promocion': cabecera[1],
                'descripcion': cabecera[2],
                'fecha_inicio': cabecera[3].strftime('%Y-%m-%d') if cabecera[3] else None,
                'fecha_fin': cabecera[4].strftime('%Y-%m-%d') if cabecera[4] else None,
                'activa': cabecera[5],
                'fecha_registro': cabecera[6].strftime('%Y-%m-%d %H:%M:%S') if cabecera[6] else None,
                'id_tipo_promocion': cabecera[7],
                'tipo_promocion': cabecera[8],
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
    # ACTIVAR/DESACTIVAR PROMOCIÓN
    # ========================================================================
    
    def cambiar_estado(self, id_promocion, activa):
        """
        Activa o desactiva una promoción
        
        Parámetros:
        - id_promocion: ID de la promoción
        - activa: True para activar, False para desactivar
        """
        con = None
        cursor = None
        
        try:
            print(f"========== DEBUG DAO: Cambiando estado de promoción {id_promocion} ==========")
            
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            # Verificar que la promoción existe
            query_check = """
            SELECT activa 
            FROM promocion 
            WHERE id_promocion = %s
            """
            cursor.execute(query_check, (id_promocion,))
            resultado = cursor.fetchone()
            
            if not resultado:
                raise ValueError(f"No se encontró la promoción N° {id_promocion}")
            
            estado_actual = resultado[0]
            print(f"DEBUG: Estado actual: {estado_actual}, Nuevo estado: {activa}")
            
            # Actualizar estado
            query_update = """
            UPDATE promocion
            SET activa = %s
            WHERE id_promocion = %s
            """
            cursor.execute(query_update, (activa, id_promocion))
            
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
    
    def obtener_tipos_promocion(self):
        """Retorna todos los tipos de promoción"""
        con = None
        cursor = None
        
        try:
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT id_tipo_promocion, descripcion
            FROM tipo_promocion
            ORDER BY descripcion
            """
            
            cursor.execute(query)
            tipos = cursor.fetchall()
            
            lista_tipos = []
            for tipo in tipos:
                lista_tipos.append({
                    'id_tipo_promocion': tipo[0],
                    'descripcion': tipo[1]
                })
            
            return lista_tipos
            
        except Exception as e:
            print(f"❌ ERROR en obtener_tipos_promocion: {str(e)}")
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