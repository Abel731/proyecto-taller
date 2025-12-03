from app.conexion.Conexion import Conexion

class AjusteStockDao:
    
    def __init__(self):
        self.conexion = Conexion()
    
    #  AGREGAR AJUSTE COMPLETO 
    def agregar_ajuste(self, datos_ajuste, detalle_ajuste):
        """
        Registra un ajuste de stock (cabecera + detalle + actualiza stock)
        
        Parámetros:
        - datos_ajuste: dict con id_empleado, id_deposito, tipo_ajuste, fecha_ajuste, observacion
        - detalle_ajuste: list de dict con id_producto, cantidad, id_motivo_ajuste
        
        Retorna:
        - id_ajuste si tiene éxito
        - None si hay error
        """
        con = None
        cursor = None
        
        try:
            print("========== DEBUG DAO AJUSTE: Iniciando agregar_ajuste ==========")
            print(f"DEBUG: datos_ajuste: {datos_ajuste}")
            print(f"DEBUG: detalle_ajuste (cantidad): {len(detalle_ajuste)}")
            
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            # 1. INSERTAR CABECERA
            print("DEBUG: Insertando cabecera...")
            query_cabecera = """
            INSERT INTO ajuste_stock 
            (id_empleado, id_deposito, tipo_ajuste, fecha_ajuste, observacion, id_estado_ajuste)
            VALUES (%s, %s, %s, %s, %s, 1)
            RETURNING id_ajuste
            """
            
            cursor.execute(query_cabecera, (
                datos_ajuste['id_empleado'],
                datos_ajuste['id_deposito'],
                datos_ajuste['tipo_ajuste'],
                datos_ajuste['fecha_ajuste'],
                datos_ajuste.get('observacion', None)
            ))
            
            id_ajuste = cursor.fetchone()[0]
            print(f"DEBUG: Ajuste insertado con ID: {id_ajuste}")
            
            # 2. INSERTAR DETALLE
            print("DEBUG: Insertando detalle...")
            query_detalle = """
            INSERT INTO ajuste_stock_detalle 
            (id_ajuste, id_producto, cantidad, id_motivo_ajuste)
            VALUES (%s, %s, %s, %s)
            """
            
            for idx, item in enumerate(detalle_ajuste, 1):
                print(f"DEBUG: Insertando producto {idx}/{len(detalle_ajuste)}: id={item['id_producto']}, cantidad={item['cantidad']}")
                cursor.execute(query_detalle, (
                    id_ajuste,
                    item['id_producto'],
                    item['cantidad'],
                    item['id_motivo_ajuste']
                ))
            
            print(f"DEBUG: Insertados {len(detalle_ajuste)} productos en el detalle")
            
            # 3. ACTUALIZAR STOCK
            print("DEBUG: Actualizando stock...")
            self._aplicar_ajuste_stock(cursor, datos_ajuste, detalle_ajuste, aplicar=True)
            
            con.commit()
            print(f"DEBUG: Transacción confirmada. ID Ajuste: {id_ajuste}")
            print("DEBUG: Conexión cerrada")
            return id_ajuste
            
        except ValueError as ve:
            if con:
                con.rollback()
                print("DEBUG: Rollback ejecutado por error de validación")
            print(f"❌ ERROR de validación: {str(ve)}")
            raise ve
            
        except Exception as e:
            if con:
                con.rollback()
                print("DEBUG: Rollback ejecutado por excepción")
            print(f"❌ ERROR en agregar_ajuste: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    #  MÉTODO PRIVADO: APLICAR/REVERTIR AJUSTE EN STOCK 
    def _aplicar_ajuste_stock(self, cursor, datos_ajuste, detalle_ajuste, aplicar=True):
        """
        Aplica o revierte el ajuste en el stock
        
        Parámetros:
        - cursor: cursor de la conexión
        - datos_ajuste: dict con tipo_ajuste e id_deposito
        - detalle_ajuste: list de dict con id_producto y cantidad
        - aplicar: True para aplicar, False para revertir
        """
        accion = "Aplicando" if aplicar else "Revirtiendo"
        print(f"DEBUG: {accion} ajuste en stock...")
        
        for idx, item in enumerate(detalle_ajuste, 1):
            print(f"DEBUG: Procesando producto {idx}/{len(detalle_ajuste)}: id={item['id_producto']}")
            
            # Verificar si existe el producto en el depósito
            query_check = """
            SELECT cantidad_actual 
            FROM stock 
            WHERE id_producto = %s AND id_deposito = %s
            """
            cursor.execute(query_check, (item['id_producto'], datos_ajuste['id_deposito']))
            resultado = cursor.fetchone()
            
            if resultado:
                stock_actual = resultado[0]
                print(f"  - Stock actual: {stock_actual}")
                
                # Determinar operación según tipo de ajuste y si aplicamos o revertimos
                if aplicar:
                    # Aplicar ajuste normal
                    if datos_ajuste['tipo_ajuste'] == 'POSITIVO':
                        nuevo_stock = stock_actual + item['cantidad']
                        print(f"  - Operación: {stock_actual} + {item['cantidad']} = {nuevo_stock}")
                    else:  # NEGATIVO
                        nuevo_stock = stock_actual - item['cantidad']
                        print(f"  - Operación: {stock_actual} - {item['cantidad']} = {nuevo_stock}")
                        if nuevo_stock < 0:
                            raise ValueError(f"El ajuste negativo resultaría en stock negativo para el producto ID {item['id_producto']}. Stock actual: {stock_actual}, Cantidad a restar: {item['cantidad']}")
                else:
                    # Revertir ajuste (operación inversa)
                    if datos_ajuste['tipo_ajuste'] == 'POSITIVO':
                        nuevo_stock = stock_actual - item['cantidad']  # Restar lo que se había sumado
                        print(f"  - Operación REVERSA: {stock_actual} - {item['cantidad']} = {nuevo_stock}")
                        if nuevo_stock < 0:
                            raise ValueError(f"No se puede anular el ajuste porque resultaría en stock negativo para el producto ID {item['id_producto']}. Stock actual: {stock_actual}, Cantidad a restar: {item['cantidad']}")
                    else:  # NEGATIVO
                        nuevo_stock = stock_actual + item['cantidad']  # Sumar lo que se había restado
                        print(f"  - Operación REVERSA: {stock_actual} + {item['cantidad']} = {nuevo_stock}")
                
                # Actualizar stock
                query_update = """
                UPDATE stock 
                SET cantidad_actual = %s
                WHERE id_producto = %s AND id_deposito = %s
                """
                cursor.execute(query_update, (nuevo_stock, item['id_producto'], datos_ajuste['id_deposito']))
                print(f"  - Stock actualizado a: {nuevo_stock}")
                
            else:
                print(f"  - Producto NO existe en el depósito")
                if aplicar:
                    # Si no existe, solo crear si es ajuste POSITIVO
                    if datos_ajuste['tipo_ajuste'] == 'POSITIVO':
                        print(f"  - Creando nuevo registro en stock con cantidad: {item['cantidad']}")
                        query_insert = """
                        INSERT INTO stock (id_producto, id_deposito, cantidad_actual)
                        VALUES (%s, %s, %s)
                        """
                        cursor.execute(query_insert, (item['id_producto'], datos_ajuste['id_deposito'], item['cantidad']))
                    else:
                        raise ValueError(f"No existe stock para el producto ID {item['id_producto']} en este depósito. No se puede realizar ajuste negativo.")
                else:
                    raise ValueError(f"No se puede anular el ajuste porque no existe stock para el producto ID {item['id_producto']} en este depósito.")
        
        print(f"DEBUG: {accion} completado exitosamente")
    
    #  ANULAR AJUSTE 
    def anular_ajuste(self, id_ajuste):
        """
        Anula un ajuste y revierte los cambios en el stock
        
        Retorna:
        - True si tiene éxito
        - False si hay error
        """
        con = None
        cursor = None
        
        try:
            print(f"========== DEBUG DAO: Anulando ajuste {id_ajuste} ==========")
            
            # ✅ CREAR NUEVA CONEXIÓN
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            # 1. Verificar que el ajuste existe y está en estado Registrado
            query_check = """
            SELECT a.id_empleado, a.id_deposito, a.tipo_ajuste, a.id_estado_ajuste
            FROM ajuste_stock a
            WHERE a.id_ajuste = %s
            """
            cursor.execute(query_check, (id_ajuste,))
            ajuste = cursor.fetchone()
            
            if not ajuste:
                raise ValueError(f"No se encontró el ajuste N° {id_ajuste}")
            
            if ajuste[3] == 2:  # 2 = Anulado
                raise ValueError(f"El ajuste N° {id_ajuste} ya está anulado")
            
            print(f"DEBUG: Ajuste encontrado - Tipo: {ajuste[2]}, Estado: {ajuste[3]}")
            
            # 2. Obtener detalle del ajuste
            query_detalle = """
            SELECT id_producto, cantidad, id_motivo_ajuste
            FROM ajuste_stock_detalle
            WHERE id_ajuste = %s
            """
            cursor.execute(query_detalle, (id_ajuste,))
            detalle_rows = cursor.fetchall()
            
            print(f"DEBUG: Productos en el ajuste: {len(detalle_rows)}")
            
            detalle_ajuste = []
            for row in detalle_rows:
                detalle_ajuste.append({
                    'id_producto': row[0],
                    'cantidad': row[1],
                    'id_motivo_ajuste': row[2]
                })
            
            # 3. Revertir el ajuste en el stock
            datos_ajuste = {
                'id_deposito': ajuste[1],
                'tipo_ajuste': ajuste[2]
            }
            
            self._aplicar_ajuste_stock(cursor, datos_ajuste, detalle_ajuste, aplicar=False)
            
            # 4. Cambiar estado a Anulado
            print("DEBUG: Actualizando estado a Anulado...")
            query_update = """
            UPDATE ajuste_stock
            SET id_estado_ajuste = 2
            WHERE id_ajuste = %s
            """
            cursor.execute(query_update, (id_ajuste,))
            
            con.commit()
            print(f"DEBUG: Ajuste {id_ajuste} anulado exitosamente")
            print("DEBUG: Conexión cerrada")
            return True
            
        except ValueError as ve:
            if con:
                con.rollback()
                print("DEBUG: Rollback ejecutado")
            print(f"❌ ERROR de validación: {str(ve)}")
            raise ve
            
        except Exception as e:
            if con:
                con.rollback()
                print("DEBUG: Rollback ejecutado")
            print(f"❌ ERROR en anular_ajuste: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    #  OBTENER TODOS LOS AJUSTES 
    def obtener_todos(self):
        """Retorna todos los ajustes con información resumida"""
        con = None
        cursor = None
        
        try:
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT * FROM vista_ajustes_stock
            ORDER BY fecha_ajuste DESC, id_ajuste DESC
            """
            
            cursor.execute(query)
            ajustes = cursor.fetchall()
            
            lista_ajustes = []
            for ajuste in ajustes:
                lista_ajustes.append({
                    'id_ajuste': ajuste[0],
                    'fecha_ajuste': ajuste[1].strftime('%Y-%m-%d') if ajuste[1] else None,
                    'empleado': ajuste[2],
                    'deposito': ajuste[3],
                    'tipo_ajuste': ajuste[4],
                    'estado': ajuste[5],
                    'id_estado_ajuste': ajuste[6],
                    'cantidad_productos': ajuste[7],
                    'observacion': ajuste[8]
                })
            
            return lista_ajustes
            
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
    
    #  OBTENER AJUSTE POR ID 
    def obtener_por_id(self, id_ajuste):
        """Retorna un ajuste completo con su detalle"""
        con = None
        cursor = None
        
        try:
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            # Obtener cabecera
            query_cabecera = """
            SELECT 
                a.id_ajuste,
                a.id_empleado,
                CONCAT(p.nombres, ' ', p.apellidos) AS empleado,
                a.id_deposito,
                d.descripcion AS deposito,
                a.tipo_ajuste,
                a.fecha_ajuste,
                a.observacion,
                a.id_estado_ajuste,
                e.descripcion AS estado
            FROM ajuste_stock a
            INNER JOIN empleados emp ON a.id_empleado = emp.id_empleado
            INNER JOIN personas p ON emp.id_empleado = p.id_persona
            INNER JOIN depositos d ON a.id_deposito = d.id_deposito
            INNER JOIN estado_ajuste e ON a.id_estado_ajuste = e.id_estado_ajuste
            WHERE a.id_ajuste = %s
            """
            
            cursor.execute(query_cabecera, (id_ajuste,))
            cabecera = cursor.fetchone()
            
            if not cabecera:
                return None
            
            # Obtener detalle
            query_detalle = """
            SELECT 
                ad.id_producto,
                pr.nombre AS producto,
                ad.cantidad,
                ad.id_motivo_ajuste,
                ma.descripcion AS motivo
            FROM ajuste_stock_detalle ad
            INNER JOIN productos pr ON ad.id_producto = pr.id_producto
            INNER JOIN motivo_ajuste ma ON ad.id_motivo_ajuste = ma.id_motivo_ajuste
            WHERE ad.id_ajuste = %s
            ORDER BY pr.nombre
            """
            
            cursor.execute(query_detalle, (id_ajuste,))
            detalle = cursor.fetchall()
            
            detalle_lista = []
            for item in detalle:
                detalle_lista.append({
                    'id_producto': item[0],
                    'producto': item[1],
                    'cantidad': item[2],
                    'id_motivo_ajuste': item[3],
                    'motivo': item[4]
                })
            
            return {
                'id_ajuste': cabecera[0],
                'id_empleado': cabecera[1],
                'empleado': cabecera[2],
                'id_deposito': cabecera[3],
                'deposito': cabecera[4],
                'tipo_ajuste': cabecera[5],
                'fecha_ajuste': cabecera[6].strftime('%Y-%m-%d') if cabecera[6] else None,
                'observacion': cabecera[7],
                'id_estado_ajuste': cabecera[8],
                'estado': cabecera[9],
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
    
    #  OBTENER PRODUCTOS DISPONIBLES 
    def obtener_productos_disponibles(self):
        """Retorna todos los productos activos"""
        con = None
        cursor = None
        
        try:
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            # ✅ QUERY CORREGIDO (sin WHERE estado)
            query = """
            SELECT id_producto, nombre
            FROM productos
            ORDER BY nombre
            """
            
            cursor.execute(query)
            productos = cursor.fetchall()
            
            lista_productos = []
            for prod in productos:
                lista_productos.append({
                    'id_producto': prod[0],
                    'nombre': prod[1]
                })
            
            return lista_productos
            
        except Exception as e:
            print(f"❌ ERROR en obtener_productos_disponibles: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    #  OBTENER MOTIVOS DE AJUSTE 
    def obtener_motivos(self):
        """Retorna todos los motivos de ajuste"""
        con = None
        cursor = None
        
        try:
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT id_motivo_ajuste, descripcion
            FROM motivo_ajuste
            ORDER BY descripcion
            """
            
            cursor.execute(query)
            motivos = cursor.fetchall()
            
            lista_motivos = []
            for motivo in motivos:
                lista_motivos.append({
                    'id_motivo_ajuste': motivo[0],
                    'descripcion': motivo[1]
                })
            
            return lista_motivos
            
        except Exception as e:
            print(f"❌ ERROR en obtener_motivos: {str(e)}")
            return []
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()