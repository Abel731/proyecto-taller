from app.conexion.Conexion import Conexion

class NotasCompraDao:
    
    def __init__(self):
        self.conexion = Conexion()
    
    # ========================================================================
    # NOTAS DE CRÉDITO
    # ========================================================================
    
    # ========== AGREGAR NOTA DE CRÉDITO ==========
    def agregar_nota_credito(self, datos_nc, detalle_nc):
        """
        Registra una nota de crédito (cabecera + detalle + actualiza stock + ajusta cuenta por pagar)
        
        Parámetros:
        - datos_nc: dict con id_compra, id_proveedor, id_empleado, id_deposito, nro_nota_credito,
                    timbrado, fecha_emision, fecha_vencimiento_timbrado, id_motivo_nc, observacion
        - detalle_nc: list de dict con id_producto, cantidad, precio_unitario, id_impuesto
        
        Retorna:
        - id_nota_credito si tiene éxito
        - None si hay error
        """
        con = None
        cursor = None
        
        try:
            print("========== DEBUG DAO NC: Iniciando agregar_nota_credito ==========")
            print(f"DEBUG: datos_nc: {datos_nc}")
            print(f"DEBUG: detalle_nc (cantidad): {len(detalle_nc)}")
            
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            # 1. INSERTAR CABECERA
            print("DEBUG: Insertando cabecera de NC...")
            query_cabecera = """
            INSERT INTO nota_credito_compra 
            (id_compra, id_proveedor, id_empleado, id_deposito, nro_nota_credito, 
             timbrado, fecha_emision, fecha_vencimiento_timbrado, id_motivo_nc, 
             observacion, id_estado_nota)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
            RETURNING id_nota_credito
            """
            
            cursor.execute(query_cabecera, (
                datos_nc['id_compra'],
                datos_nc['id_proveedor'],
                datos_nc['id_empleado'],
                datos_nc['id_deposito'],
                datos_nc['nro_nota_credito'],
                datos_nc['timbrado'],
                datos_nc['fecha_emision'],
                datos_nc['fecha_vencimiento_timbrado'],
                datos_nc['id_motivo_nc'],
                datos_nc.get('observacion', None)
            ))
            
            id_nota_credito = cursor.fetchone()[0]
            print(f"DEBUG: NC insertada con ID: {id_nota_credito}")
            
            # 2. INSERTAR DETALLE
            print("DEBUG: Insertando detalle de NC...")
            query_detalle = """
            INSERT INTO nota_credito_compra_detalle 
            (id_nota_credito, id_producto, cantidad, precio_unitario, id_impuesto)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            total_devuelto = 0
            for idx, item in enumerate(detalle_nc, 1):
                print(f"DEBUG: Insertando producto {idx}/{len(detalle_nc)}: id={item['id_producto']}, cantidad={item['cantidad']}")
                cursor.execute(query_detalle, (
                    id_nota_credito,
                    item['id_producto'],
                    item['cantidad'],
                    item['precio_unitario'],
                    item['id_impuesto']
                ))
                
                # Calcular total
                subtotal = item['cantidad'] * item['precio_unitario']
                # Obtener tasa de IVA
                cursor.execute("SELECT tasa FROM impuestos WHERE id_impuesto = %s", (item['id_impuesto'],))
                tasa_iva = cursor.fetchone()[0]
                iva = subtotal * (tasa_iva / 100)
                total_devuelto += subtotal + iva
            
            print(f"DEBUG: Insertados {len(detalle_nc)} productos en NC")
            print(f"DEBUG: Total devuelto: {total_devuelto}")
            
            # 3. ACTUALIZAR STOCK (RESTAR porque es devolución)
            print("DEBUG: Actualizando stock (restando)...")
            for item in detalle_nc:
                query_check_stock = """
                SELECT cantidad_actual 
                FROM stock 
                WHERE id_producto = %s AND id_deposito = %s
                """
                cursor.execute(query_check_stock, (item['id_producto'], datos_nc['id_deposito']))
                resultado = cursor.fetchone()
                
                if resultado:
                    stock_actual = resultado[0]
                    nuevo_stock = stock_actual - item['cantidad']
                    
                    print(f"  - Producto {item['id_producto']}: {stock_actual} - {item['cantidad']} = {nuevo_stock}")
                    
                    if nuevo_stock < 0:
                        raise ValueError(f"ERROR: No hay suficiente stock para devolver el producto ID {item['id_producto']}. Stock actual: {stock_actual}, Cantidad a devolver: {item['cantidad']}")
                    
                    query_update_stock = """
                    UPDATE stock 
                    SET cantidad_actual = %s
                    WHERE id_producto = %s AND id_deposito = %s
                    """
                    cursor.execute(query_update_stock, (nuevo_stock, item['id_producto'], datos_nc['id_deposito']))
                else:
                    raise ValueError(f"ERROR: No existe stock para el producto ID {item['id_producto']} en este depósito")
            
            print("DEBUG: Stock actualizado")
            
            # 4. AJUSTAR CUENTA POR PAGAR (si la compra fue a crédito)
            print("DEBUG: Verificando si la compra fue a crédito...")
            query_check_credito = """
            SELECT c.id_tipo_factura, cpp.id_cuenta_pagar, cpp.saldo
            FROM compra c
            LEFT JOIN cuentas_por_pagar cpp ON c.id_compra = cpp.id_compra
            WHERE c.id_compra = %s
            """
            cursor.execute(query_check_credito, (datos_nc['id_compra'],))
            compra_info = cursor.fetchone()
            
            if compra_info and compra_info[0] == 2:  # 2 = Crédito
                print(f"DEBUG: Compra a crédito. Ajustando cuenta por pagar...")
                id_cuenta_pagar = compra_info[1]
                saldo_actual = compra_info[2]
                nuevo_saldo = saldo_actual - total_devuelto
                
                print(f"  - Saldo actual: {saldo_actual}")
                print(f"  - Total NC: {total_devuelto}")
                print(f"  - Nuevo saldo: {nuevo_saldo}")
                
                if nuevo_saldo < 0:
                    print("  - ADVERTENCIA: El nuevo saldo es negativo (NC mayor que deuda)")
                    nuevo_saldo = 0
                
                query_update_cpp = """
                UPDATE cuentas_por_pagar
                SET saldo = %s
                WHERE id_cuenta_pagar = %s
                """
                cursor.execute(query_update_cpp, (nuevo_saldo, id_cuenta_pagar))
                print("DEBUG: Cuenta por pagar actualizada")
            else:
                print("DEBUG: Compra al contado, no hay cuenta por pagar que ajustar")
            
            con.commit()
            print(f"DEBUG: Transacción confirmada. ID NC: {id_nota_credito}")
            return id_nota_credito
            
        except ValueError as ve:
            if con:
                con.rollback()
            print(f"❌ ERROR de validación: {str(ve)}")
            raise ve
            
        except Exception as e:
            if con:
                con.rollback()
            print(f"❌ ERROR en agregar_nota_credito: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    # ========== ANULAR NOTA DE CRÉDITO ==========
    def anular_nota_credito(self, id_nota_credito):
        """
        Anula una nota de crédito y revierte los cambios en stock y cuenta por pagar
        
        Retorna:
        - True si tiene éxito
        - False si hay error
        """
        con = None
        cursor = None
        
        try:
            print(f"========== DEBUG DAO: Anulando NC {id_nota_credito} ==========")
            
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            # 1. Verificar que existe y está en estado Registrada
            query_check = """
            SELECT id_compra, id_deposito, id_estado_nota
            FROM nota_credito_compra
            WHERE id_nota_credito = %s
            """
            cursor.execute(query_check, (id_nota_credito,))
            nc = cursor.fetchone()
            
            if not nc:
                raise ValueError(f"No se encontró la NC N° {id_nota_credito}")
            
            if nc[2] == 2:  # 2 = Anulada
                raise ValueError(f"La NC N° {id_nota_credito} ya está anulada")
            
            id_compra = nc[0]
            id_deposito = nc[1]
            
            print(f"DEBUG: NC encontrada - Compra: {id_compra}, Depósito: {id_deposito}")
            
            # 2. Obtener detalle
            query_detalle = """
            SELECT ncd.id_producto, ncd.cantidad, ncd.precio_unitario, ncd.id_impuesto
            FROM nota_credito_compra_detalle ncd
            WHERE ncd.id_nota_credito = %s
            """
            cursor.execute(query_detalle, (id_nota_credito,))
            detalle = cursor.fetchall()
            
            print(f"DEBUG: Productos en NC: {len(detalle)}")
            
            # 3. Revertir stock (SUMAR lo que se había restado)
            print("DEBUG: Revirtiendo stock (sumando)...")
            total_revertido = 0
            for item in detalle:
                id_producto = item[0]
                cantidad = item[1]
                precio_unitario = item[2]
                id_impuesto = item[3]
                
                query_update_stock = """
                UPDATE stock 
                SET cantidad_actual = cantidad_actual + %s
                WHERE id_producto = %s AND id_deposito = %s
                """
                cursor.execute(query_update_stock, (cantidad, id_producto, id_deposito))
                print(f"  - Producto {id_producto}: +{cantidad}")
                
                # Calcular total
                subtotal = cantidad * precio_unitario
                cursor.execute("SELECT tasa FROM impuestos WHERE id_impuesto = %s", (id_impuesto,))
                tasa_iva = cursor.fetchone()[0]
                iva = subtotal * (tasa_iva / 100)
                total_revertido += subtotal + iva
            
            print(f"DEBUG: Stock revertido. Total: {total_revertido}")
            
            # 4. Revertir cuenta por pagar (si aplica)
            query_check_credito = """
            SELECT cpp.id_cuenta_pagar, cpp.saldo
            FROM compra c
            LEFT JOIN cuentas_por_pagar cpp ON c.id_compra = cpp.id_compra
            WHERE c.id_compra = %s AND c.id_tipo_factura = 2
            """
            cursor.execute(query_check_credito, (id_compra,))
            cpp_info = cursor.fetchone()
            
            if cpp_info:
                print("DEBUG: Revirtiendo cuenta por pagar...")
                id_cuenta_pagar = cpp_info[0]
                saldo_actual = cpp_info[1]
                nuevo_saldo = saldo_actual + total_revertido
                
                print(f"  - Saldo actual: {saldo_actual}")
                print(f"  - Total a revertir: {total_revertido}")
                print(f"  - Nuevo saldo: {nuevo_saldo}")
                
                query_update_cpp = """
                UPDATE cuentas_por_pagar
                SET saldo = %s
                WHERE id_cuenta_pagar = %s
                """
                cursor.execute(query_update_cpp, (nuevo_saldo, id_cuenta_pagar))
                print("DEBUG: Cuenta por pagar revertida")
            
            # 5. Cambiar estado a Anulada
            query_update = """
            UPDATE nota_credito_compra
            SET id_estado_nota = 2
            WHERE id_nota_credito = %s
            """
            cursor.execute(query_update, (id_nota_credito,))
            
            con.commit()
            print(f"DEBUG: NC {id_nota_credito} anulada exitosamente")
            return True
            
        except ValueError as ve:
            if con:
                con.rollback()
            print(f"❌ ERROR de validación: {str(ve)}")
            raise ve
            
        except Exception as e:
            if con:
                con.rollback()
            print(f"❌ ERROR en anular_nota_credito: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()


    # ========================================================================
    # NOTAS DE DÉBITO
    # ========================================================================
    
    # ========== AGREGAR NOTA DE DÉBITO ==========
    def agregar_nota_debito(self, datos_nd, detalle_nd):
        """
        Registra una nota de débito (cabecera + detalle + actualiza stock si aplica + ajusta cuenta por pagar)
        
        Parámetros:
        - datos_nd: dict con id_compra, id_proveedor, id_empleado, id_deposito, nro_nota_debito,
                    timbrado, fecha_emision, fecha_vencimiento_timbrado, id_motivo_nd, 
                    afecta_stock, observacion
        - detalle_nd: list de dict con id_producto, cantidad, precio_unitario, id_impuesto
        
        Retorna:
        - id_nota_debito si tiene éxito
        - None si hay error
        """
        con = None
        cursor = None
        
        try:
            print("========== DEBUG DAO ND: Iniciando agregar_nota_debito ==========")
            print(f"DEBUG: datos_nd: {datos_nd}")
            print(f"DEBUG: detalle_nd (cantidad): {len(detalle_nd)}")
            print(f"DEBUG: Afecta stock: {datos_nd['afecta_stock']}")
            
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            # 1. INSERTAR CABECERA
            print("DEBUG: Insertando cabecera de ND...")
            query_cabecera = """
            INSERT INTO nota_debito_compra 
            (id_compra, id_proveedor, id_empleado, id_deposito, nro_nota_debito, 
             timbrado, fecha_emision, fecha_vencimiento_timbrado, id_motivo_nd, 
             afecta_stock, observacion, id_estado_nota)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
            RETURNING id_nota_debito
            """
            
            cursor.execute(query_cabecera, (
                datos_nd['id_compra'],
                datos_nd['id_proveedor'],
                datos_nd['id_empleado'],
                datos_nd.get('id_deposito', None),
                datos_nd['nro_nota_debito'],
                datos_nd['timbrado'],
                datos_nd['fecha_emision'],
                datos_nd['fecha_vencimiento_timbrado'],
                datos_nd['id_motivo_nd'],
                datos_nd['afecta_stock'],
                datos_nd.get('observacion', None)
            ))
            
            id_nota_debito = cursor.fetchone()[0]
            print(f"DEBUG: ND insertada con ID: {id_nota_debito}")
            
            # 2. INSERTAR DETALLE
            print("DEBUG: Insertando detalle de ND...")
            query_detalle = """
            INSERT INTO nota_debito_compra_detalle 
            (id_nota_debito, id_producto, cantidad, precio_unitario, id_impuesto)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            total_cargo = 0
            for idx, item in enumerate(detalle_nd, 1):
                print(f"DEBUG: Insertando producto {idx}/{len(detalle_nd)}: id={item['id_producto']}, cantidad={item['cantidad']}")
                cursor.execute(query_detalle, (
                    id_nota_debito,
                    item['id_producto'],
                    item['cantidad'],
                    item['precio_unitario'],
                    item['id_impuesto']
                ))
                
                # Calcular total
                subtotal = item['cantidad'] * item['precio_unitario']
                # Obtener tasa de IVA
                cursor.execute("SELECT tasa FROM impuestos WHERE id_impuesto = %s", (item['id_impuesto'],))
                tasa_iva = cursor.fetchone()[0]
                iva = subtotal * (tasa_iva / 100)
                total_cargo += subtotal + iva
            
            print(f"DEBUG: Insertados {len(detalle_nd)} productos en ND")
            print(f"DEBUG: Total cargo: {total_cargo}")
            
            # 3. ACTUALIZAR STOCK (SUMAR si afecta_stock = TRUE)
            if datos_nd['afecta_stock']:
                print("DEBUG: Actualizando stock (sumando mercadería adicional)...")
                
                if not datos_nd.get('id_deposito'):
                    raise ValueError("ERROR: Si afecta_stock es TRUE, debe especificar un depósito")
                
                for item in detalle_nd:
                    query_check_stock = """
                    SELECT cantidad_actual 
                    FROM stock 
                    WHERE id_producto = %s AND id_deposito = %s
                    """
                    cursor.execute(query_check_stock, (item['id_producto'], datos_nd['id_deposito']))
                    resultado = cursor.fetchone()
                    
                    if resultado:
                        stock_actual = resultado[0]
                        nuevo_stock = stock_actual + item['cantidad']
                        
                        print(f"  - Producto {item['id_producto']}: {stock_actual} + {item['cantidad']} = {nuevo_stock}")
                        
                        query_update_stock = """
                        UPDATE stock 
                        SET cantidad_actual = %s
                        WHERE id_producto = %s AND id_deposito = %s
                        """
                        cursor.execute(query_update_stock, (nuevo_stock, item['id_producto'], datos_nd['id_deposito']))
                    else:
                        # Crear nuevo registro si no existe
                        print(f"  - Producto {item['id_producto']}: Creando nuevo stock con cantidad {item['cantidad']}")
                        query_insert_stock = """
                        INSERT INTO stock (id_producto, id_deposito, cantidad_actual)
                        VALUES (%s, %s, %s)
                        """
                        cursor.execute(query_insert_stock, (item['id_producto'], datos_nd['id_deposito'], item['cantidad']))
                
                print("DEBUG: Stock actualizado")
            else:
                print("DEBUG: No afecta stock (solo cargos administrativos)")
            
            # 4. AJUSTAR CUENTA POR PAGAR (si la compra fue a crédito)
            print("DEBUG: Verificando si la compra fue a crédito...")
            query_check_credito = """
            SELECT c.id_tipo_factura, cpp.id_cuenta_pagar, cpp.saldo
            FROM compra c
            LEFT JOIN cuentas_por_pagar cpp ON c.id_compra = cpp.id_compra
            WHERE c.id_compra = %s
            """
            cursor.execute(query_check_credito, (datos_nd['id_compra'],))
            compra_info = cursor.fetchone()
            
            if compra_info and compra_info[0] == 2:  # 2 = Crédito
                print(f"DEBUG: Compra a crédito. Aumentando cuenta por pagar...")
                id_cuenta_pagar = compra_info[1]
                saldo_actual = compra_info[2]
                nuevo_saldo = saldo_actual + total_cargo
                
                print(f"  - Saldo actual: {saldo_actual}")
                print(f"  - Total ND: {total_cargo}")
                print(f"  - Nuevo saldo: {nuevo_saldo}")
                
                query_update_cpp = """
                UPDATE cuentas_por_pagar
                SET saldo = %s
                WHERE id_cuenta_pagar = %s
                """
                cursor.execute(query_update_cpp, (nuevo_saldo, id_cuenta_pagar))
                print("DEBUG: Cuenta por pagar actualizada")
            else:
                print("DEBUG: Compra al contado, no hay cuenta por pagar que ajustar")
            
            con.commit()
            print(f"DEBUG: Transacción confirmada. ID ND: {id_nota_debito}")
            return id_nota_debito
            
        except ValueError as ve:
            if con:
                con.rollback()
            print(f"❌ ERROR de validación: {str(ve)}")
            raise ve
            
        except Exception as e:
            if con:
                con.rollback()
            print(f"❌ ERROR en agregar_nota_debito: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    # ========== ANULAR NOTA DE DÉBITO ==========
    def anular_nota_debito(self, id_nota_debito):
        """
        Anula una nota de débito y revierte los cambios en stock (si aplica) y cuenta por pagar
        
        Retorna:
        - True si tiene éxito
        - False si hay error
        """
        con = None
        cursor = None
        
        try:
            print(f"========== DEBUG DAO: Anulando ND {id_nota_debito} ==========")
            
            conexion = Conexion()
            con = conexion.getConexion()
            cursor = con.cursor()
            
            # 1. Verificar que existe y está en estado Registrada
            query_check = """
            SELECT id_compra, id_deposito, afecta_stock, id_estado_nota
            FROM nota_debito_compra
            WHERE id_nota_debito = %s
            """
            cursor.execute(query_check, (id_nota_debito,))
            nd = cursor.fetchone()
            
            if not nd:
                raise ValueError(f"No se encontró la ND N° {id_nota_debito}")
            
            if nd[3] == 2:  # 2 = Anulada
                raise ValueError(f"La ND N° {id_nota_debito} ya está anulada")
            
            id_compra = nd[0]
            id_deposito = nd[1]
            afecta_stock = nd[2]
            
            print(f"DEBUG: ND encontrada - Compra: {id_compra}, Afecta stock: {afecta_stock}")
            
            # 2. Obtener detalle
            query_detalle = """
            SELECT ndd.id_producto, ndd.cantidad, ndd.precio_unitario, ndd.id_impuesto
            FROM nota_debito_compra_detalle ndd
            WHERE ndd.id_nota_debito = %s
            """
            cursor.execute(query_detalle, (id_nota_debito,))
            detalle = cursor.fetchall()
            
            print(f"DEBUG: Productos en ND: {len(detalle)}")
            
            # 3. Revertir stock si aplica (RESTAR lo que se había sumado)
            total_revertido = 0
            if afecta_stock:
                print("DEBUG: Revirtiendo stock (restando)...")
                
                for item in detalle:
                    id_producto = item[0]
                    cantidad = item[1]
                    precio_unitario = item[2]
                    id_impuesto = item[3]
                    
                    query_check_stock = """
                    SELECT cantidad_actual 
                    FROM stock 
                    WHERE id_producto = %s AND id_deposito = %s
                    """
                    cursor.execute(query_check_stock, (id_producto, id_deposito))
                    resultado = cursor.fetchone()
                    
                    if resultado:
                        stock_actual = resultado[0]
                        nuevo_stock = stock_actual - cantidad
                        
                        print(f"  - Producto {id_producto}: {stock_actual} - {cantidad} = {nuevo_stock}")
                        
                        if nuevo_stock < 0:
                            raise ValueError(f"ERROR: No se puede anular la ND porque resultaría en stock negativo para el producto ID {id_producto}. Stock actual: {stock_actual}, Cantidad a restar: {cantidad}")
                        
                        query_update_stock = """
                        UPDATE stock 
                        SET cantidad_actual = %s
                        WHERE id_producto = %s AND id_deposito = %s
                        """
                        cursor.execute(query_update_stock, (nuevo_stock, id_producto, id_deposito))
                    else:
                        raise ValueError(f"ERROR: No existe stock para el producto ID {id_producto} en este depósito")
                    
                    # Calcular total
                    subtotal = cantidad * precio_unitario
                    cursor.execute("SELECT tasa FROM impuestos WHERE id_impuesto = %s", (id_impuesto,))
                    tasa_iva = cursor.fetchone()[0]
                    iva = subtotal * (tasa_iva / 100)
                    total_revertido += subtotal + iva
                
                print(f"DEBUG: Stock revertido")
            else:
                print("DEBUG: No afecta stock, calculando total para cuenta por pagar...")
                for item in detalle:
                    subtotal = item[1] * item[2]
                    cursor.execute("SELECT tasa FROM impuestos WHERE id_impuesto = %s", (item[3],))
                    tasa_iva = cursor.fetchone()[0]
                    iva = subtotal * (tasa_iva / 100)
                    total_revertido += subtotal + iva
            
            print(f"DEBUG: Total a revertir: {total_revertido}")
            
            # 4. Revertir cuenta por pagar (si aplica)
            query_check_credito = """
            SELECT cpp.id_cuenta_pagar, cpp.saldo
            FROM compra c
            LEFT JOIN cuentas_por_pagar cpp ON c.id_compra = cpp.id_compra
            WHERE c.id_compra = %s AND c.id_tipo_factura = 2
            """
            cursor.execute(query_check_credito, (id_compra,))
            cpp_info = cursor.fetchone()
            
            if cpp_info:
                print("DEBUG: Revirtiendo cuenta por pagar...")
                id_cuenta_pagar = cpp_info[0]
                saldo_actual = cpp_info[1]
                nuevo_saldo = saldo_actual - total_revertido
                
                print(f"  - Saldo actual: {saldo_actual}")
                print(f"  - Total a revertir: {total_revertido}")
                print(f"  - Nuevo saldo: {nuevo_saldo}")
                
                if nuevo_saldo < 0:
                    print("  - ADVERTENCIA: El nuevo saldo es negativo")
                    nuevo_saldo = 0
                
                query_update_cpp = """
                UPDATE cuentas_por_pagar
                SET saldo = %s
                WHERE id_cuenta_pagar = %s
                """
                cursor.execute(query_update_cpp, (nuevo_saldo, id_cuenta_pagar))
                print("DEBUG: Cuenta por pagar revertida")
            
            # 5. Cambiar estado a Anulada
            query_update = """
            UPDATE nota_debito_compra
            SET id_estado_nota = 2
            WHERE id_nota_debito = %s
            """
            cursor.execute(query_update, (id_nota_debito,))
            
            con.commit()
            print(f"DEBUG: ND {id_nota_debito} anulada exitosamente")
            return True
            
        except ValueError as ve:
            if con:
                con.rollback()
            print(f"❌ ERROR de validación: {str(ve)}")
            raise ve
            
        except Exception as e:
            if con:
                con.rollback()
            print(f"❌ ERROR en anular_nota_debito: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()            



    # ========================================================================
    # CONSULTAS - NOTAS DE CRÉDITO
    # ========================================================================
    
    # ========== OBTENER TODAS LAS NOTAS DE CRÉDITO ==========
    def obtener_todas_nc(self):
        """Retorna todas las notas de crédito con información resumida"""
        con = None
        cursor = None
        
        try:
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT * FROM vista_notas_credito
            ORDER BY fecha_emision DESC, id_nota_credito DESC
            """
            
            cursor.execute(query)
            notas = cursor.fetchall()
            
            lista_notas = []
            for nota in notas:
                lista_notas.append({
                    'id_nota_credito': nota[0],
                    'nro_nota_credito': nota[1],
                    'fecha_emision': nota[2].strftime('%Y-%m-%d') if nota[2] else None,
                    'factura_origen': nota[3],
                    'proveedor': nota[4],
                    'empleado': nota[5],
                    'deposito': nota[6],
                    'motivo': nota[7],
                    'estado': nota[8],
                    'id_estado_nota': nota[9],
                    'cantidad_productos': nota[10],
                    'observacion': nota[11]
                })
            
            return lista_notas
            
        except Exception as e:
            print(f"❌ ERROR en obtener_todas_nc: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    # ========== OBTENER NOTA DE CRÉDITO POR ID ==========
    def obtener_nc_por_id(self, id_nota_credito):
        """Retorna una nota de crédito completa con su detalle"""
        con = None
        cursor = None
        
        try:
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            # Obtener cabecera
            query_cabecera = """
            SELECT 
                nc.id_nota_credito,
                nc.nro_nota_credito,
                nc.fecha_emision,
                nc.timbrado,
                nc.fecha_vencimiento_timbrado,
                nc.id_compra,
                c.nro_factura,
                nc.id_proveedor,
                prov.razon_social,
                nc.id_empleado,
                CONCAT(p.nombres, ' ', p.apellidos) AS empleado,
                nc.id_deposito,
                d.descripcion AS deposito,
                nc.id_motivo_nc,
                m.descripcion AS motivo,
                nc.observacion,
                nc.id_estado_nota,
                e.descripcion AS estado
            FROM nota_credito_compra nc
            INNER JOIN compra c ON nc.id_compra = c.id_compra
            INNER JOIN proveedores prov ON nc.id_proveedor = prov.id_proveedor
            INNER JOIN empleados emp ON nc.id_empleado = emp.id_empleado
            INNER JOIN personas p ON emp.id_empleado = p.id_persona
            INNER JOIN depositos d ON nc.id_deposito = d.id_deposito
            INNER JOIN motivo_nota_credito m ON nc.id_motivo_nc = m.id_motivo_nc
            INNER JOIN estado_nota e ON nc.id_estado_nota = e.id_estado_nota
            WHERE nc.id_nota_credito = %s
            """
            
            cursor.execute(query_cabecera, (id_nota_credito,))
            cabecera = cursor.fetchone()
            
            if not cabecera:
                return None
            
            # Obtener detalle
            query_detalle = """
            SELECT 
                ncd.id_producto,
                pr.nombre AS producto,
                ncd.cantidad,
                ncd.precio_unitario,
                ncd.id_impuesto,
                imp.descripcion AS impuesto,
                imp.tasa
            FROM nota_credito_compra_detalle ncd
            INNER JOIN productos pr ON ncd.id_producto = pr.id_producto
            INNER JOIN impuestos imp ON ncd.id_impuesto = imp.id_impuesto
            WHERE ncd.id_nota_credito = %s
            ORDER BY pr.nombre
            """
            
            cursor.execute(query_detalle, (id_nota_credito,))
            detalle = cursor.fetchall()
            
            detalle_lista = []
            total_subtotal = 0
            total_iva = 0
            
            for item in detalle:
                subtotal = item[2] * item[3]
                iva = subtotal * (item[6] / 100)
                total = subtotal + iva
                
                total_subtotal += subtotal
                total_iva += iva
                
                detalle_lista.append({
                    'id_producto': item[0],
                    'producto': item[1],
                    'cantidad': item[2],
                    'precio_unitario': float(item[3]),
                    'id_impuesto': item[4],
                    'impuesto': item[5],
                    'tasa_iva': float(item[6]),
                    'subtotal': float(subtotal),
                    'iva': float(iva),
                    'total': float(total)
                })
            
            return {
                'id_nota_credito': cabecera[0],
                'nro_nota_credito': cabecera[1],
                'fecha_emision': cabecera[2].strftime('%Y-%m-%d') if cabecera[2] else None,
                'timbrado': cabecera[3],
                'fecha_vencimiento_timbrado': cabecera[4].strftime('%Y-%m-%d') if cabecera[4] else None,
                'id_compra': cabecera[5],
                'factura_origen': cabecera[6],
                'id_proveedor': cabecera[7],
                'proveedor': cabecera[8],
                'id_empleado': cabecera[9],
                'empleado': cabecera[10],
                'id_deposito': cabecera[11],
                'deposito': cabecera[12],
                'id_motivo_nc': cabecera[13],
                'motivo': cabecera[14],
                'observacion': cabecera[15],
                'id_estado_nota': cabecera[16],
                'estado': cabecera[17],
                'detalle': detalle_lista,
                'total_subtotal': float(total_subtotal),
                'total_iva': float(total_iva),
                'total_general': float(total_subtotal + total_iva)
            }
            
        except Exception as e:
            print(f"❌ ERROR en obtener_nc_por_id: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    # ========================================================================
    # CONSULTAS - NOTAS DE DÉBITO
    # ========================================================================
    
    # ========== OBTENER TODAS LAS NOTAS DE DÉBITO ==========
    def obtener_todas_nd(self):
        """Retorna todas las notas de débito con información resumida"""
        con = None
        cursor = None
        
        try:
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT * FROM vista_notas_debito
            ORDER BY fecha_emision DESC, id_nota_debito DESC
            """
            
            cursor.execute(query)
            notas = cursor.fetchall()
            
            lista_notas = []
            for nota in notas:
                lista_notas.append({
                    'id_nota_debito': nota[0],
                    'nro_nota_debito': nota[1],
                    'fecha_emision': nota[2].strftime('%Y-%m-%d') if nota[2] else None,
                    'factura_origen': nota[3],
                    'proveedor': nota[4],
                    'empleado': nota[5],
                    'deposito': nota[6] if nota[6] else 'N/A',
                    'motivo': nota[7],
                    'afecta_stock': nota[8],
                    'estado': nota[9],
                    'id_estado_nota': nota[10],
                    'cantidad_productos': nota[11],
                    'observacion': nota[12]
                })
            
            return lista_notas
            
        except Exception as e:
            print(f"❌ ERROR en obtener_todas_nd: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    # ========== OBTENER NOTA DE DÉBITO POR ID ==========
    def obtener_nd_por_id(self, id_nota_debito):
        """Retorna una nota de débito completa con su detalle"""
        con = None
        cursor = None
        
        try:
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            # Obtener cabecera
            query_cabecera = """
            SELECT 
                nd.id_nota_debito,
                nd.nro_nota_debito,
                nd.fecha_emision,
                nd.timbrado,
                nd.fecha_vencimiento_timbrado,
                nd.id_compra,
                c.nro_factura,
                nd.id_proveedor,
                prov.razon_social,
                nd.id_empleado,
                CONCAT(p.nombres, ' ', p.apellidos) AS empleado,
                nd.id_deposito,
                d.descripcion AS deposito,
                nd.id_motivo_nd,
                m.descripcion AS motivo,
                nd.afecta_stock,
                nd.observacion,
                nd.id_estado_nota,
                e.descripcion AS estado
            FROM nota_debito_compra nd
            INNER JOIN compra c ON nd.id_compra = c.id_compra
            INNER JOIN proveedores prov ON nd.id_proveedor = prov.id_proveedor
            INNER JOIN empleados emp ON nd.id_empleado = emp.id_empleado
            INNER JOIN personas p ON emp.id_empleado = p.id_persona
            LEFT JOIN depositos d ON nd.id_deposito = d.id_deposito
            INNER JOIN motivo_nota_debito m ON nd.id_motivo_nd = m.id_motivo_nd
            INNER JOIN estado_nota e ON nd.id_estado_nota = e.id_estado_nota
            WHERE nd.id_nota_debito = %s
            """
            
            cursor.execute(query_cabecera, (id_nota_debito,))
            cabecera = cursor.fetchone()
            
            if not cabecera:
                return None
            
            # Obtener detalle
            query_detalle = """
            SELECT 
                ndd.id_producto,
                pr.nombre AS producto,
                ndd.cantidad,
                ndd.precio_unitario,
                ndd.id_impuesto,
                imp.descripcion AS impuesto,
                imp.tasa
            FROM nota_debito_compra_detalle ndd
            INNER JOIN productos pr ON ndd.id_producto = pr.id_producto
            INNER JOIN impuestos imp ON ndd.id_impuesto = imp.id_impuesto
            WHERE ndd.id_nota_debito = %s
            ORDER BY pr.nombre
            """
            
            cursor.execute(query_detalle, (id_nota_debito,))
            detalle = cursor.fetchall()
            
            detalle_lista = []
            total_subtotal = 0
            total_iva = 0
            
            for item in detalle:
                subtotal = item[2] * item[3]
                iva = subtotal * (item[6] / 100)
                total = subtotal + iva
                
                total_subtotal += subtotal
                total_iva += iva
                
                detalle_lista.append({
                    'id_producto': item[0],
                    'producto': item[1],
                    'cantidad': item[2],
                    'precio_unitario': float(item[3]),
                    'id_impuesto': item[4],
                    'impuesto': item[5],
                    'tasa_iva': float(item[6]),
                    'subtotal': float(subtotal),
                    'iva': float(iva),
                    'total': float(total)
                })
            
            return {
                'id_nota_debito': cabecera[0],
                'nro_nota_debito': cabecera[1],
                'fecha_emision': cabecera[2].strftime('%Y-%m-%d') if cabecera[2] else None,
                'timbrado': cabecera[3],
                'fecha_vencimiento_timbrado': cabecera[4].strftime('%Y-%m-%d') if cabecera[4] else None,
                'id_compra': cabecera[5],
                'factura_origen': cabecera[6],
                'id_proveedor': cabecera[7],
                'proveedor': cabecera[8],
                'id_empleado': cabecera[9],
                'empleado': cabecera[10],
                'id_deposito': cabecera[11],
                'deposito': cabecera[12] if cabecera[12] else 'N/A',
                'id_motivo_nd': cabecera[13],
                'motivo': cabecera[14],
                'afecta_stock': cabecera[15],
                'observacion': cabecera[16],
                'id_estado_nota': cabecera[17],
                'estado': cabecera[18],
                'detalle': detalle_lista,
                'total_subtotal': float(total_subtotal),
                'total_iva': float(total_iva),
                'total_general': float(total_subtotal + total_iva)
            }
            
        except Exception as e:
            print(f"❌ ERROR en obtener_nd_por_id: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    # ========================================================================
    # CONSULTAS AUXILIARES
    # ========================================================================
    
    # ========== OBTENER COMPRAS DISPONIBLES PARA NOTAS ==========
    def obtener_compras_finalizadas(self):
        """Retorna compras en estado Finalizada que pueden tener notas"""
        con = None
        cursor = None
        
        try:
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT 
                c.id_compra,
                c.nro_factura,
                c.fecha_compra,
                prov.razon_social AS proveedor,
                CASE WHEN c.id_tipo_factura = 1 THEN 'Contado' ELSE 'Crédito' END AS tipo
            FROM compra c
            INNER JOIN proveedores prov ON c.id_proveedor = prov.id_proveedor
            WHERE c.id_estado_compra = 2
            ORDER BY c.fecha_compra DESC, c.id_compra DESC
            """
            
            cursor.execute(query)
            compras = cursor.fetchall()
            
            lista_compras = []
            for compra in compras:
                lista_compras.append({
                    'id_compra': compra[0],
                    'nro_factura': compra[1],
                    'fecha_compra': compra[2].strftime('%Y-%m-%d') if compra[2] else None,
                    'proveedor': compra[3],
                    'tipo': compra[4]
                })
            
            return lista_compras
            
        except Exception as e:
            print(f"❌ ERROR en obtener_compras_finalizadas: {str(e)}")
            return []
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    # ========== OBTENER PRODUCTOS DE UNA COMPRA ==========
    def obtener_productos_compra(self, id_compra):
        """Retorna los productos de una compra específica"""
        con = None
        cursor = None
        
        try:
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT 
                cd.id_producto,
                pr.nombre,
                cd.cantidad,
                cd.precio_unitario,
                cd.id_impuesto,
                imp.descripcion AS impuesto,
                imp.tasa
            FROM compra_detalle cd
            INNER JOIN productos pr ON cd.id_producto = pr.id_producto
            INNER JOIN impuestos imp ON cd.id_impuesto = imp.id_impuesto
            WHERE cd.id_compra = %s
            ORDER BY pr.nombre
            """
            
            cursor.execute(query, (id_compra,))
            productos = cursor.fetchall()
            
            lista_productos = []
            for prod in productos:
                lista_productos.append({
                    'id_producto': prod[0],
                    'nombre': prod[1],
                    'cantidad': prod[2],
                    'precio_unitario': float(prod[3]),
                    'id_impuesto': prod[4],
                    'impuesto': prod[5],
                    'tasa': float(prod[6])
                })
            
            return lista_productos
            
        except Exception as e:
            print(f"❌ ERROR en obtener_productos_compra: {str(e)}")
            return []
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    # ========== OBTENER MOTIVOS DE NOTA DE CRÉDITO ==========
    def obtener_motivos_nc(self):
        """Retorna todos los motivos de nota de crédito"""
        con = None
        cursor = None
        
        try:
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT id_motivo_nc, descripcion
            FROM motivo_nota_credito
            ORDER BY descripcion
            """
            
            cursor.execute(query)
            motivos = cursor.fetchall()
            
            lista_motivos = []
            for motivo in motivos:
                lista_motivos.append({
                    'id_motivo_nc': motivo[0],
                    'descripcion': motivo[1]
                })
            
            return lista_motivos
            
        except Exception as e:
            print(f"❌ ERROR en obtener_motivos_nc: {str(e)}")
            return []
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    # ========== OBTENER MOTIVOS DE NOTA DE DÉBITO ==========
    def obtener_motivos_nd(self):
        """Retorna todos los motivos de nota de débito"""
        con = None
        cursor = None
        
        try:
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT id_motivo_nd, descripcion
            FROM motivo_nota_debito
            ORDER BY descripcion
            """
            
            cursor.execute(query)
            motivos = cursor.fetchall()
            
            lista_motivos = []
            for motivo in motivos:
                lista_motivos.append({
                    'id_motivo_nd': motivo[0],
                    'descripcion': motivo[1]
                })
            
            return lista_motivos
            
        except Exception as e:
            print(f"❌ ERROR en obtener_motivos_nd: {str(e)}")
            return []
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()            