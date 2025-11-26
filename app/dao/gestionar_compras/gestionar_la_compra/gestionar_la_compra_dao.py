from app.conexion.Conexion import Conexion

class CompraDao:
    
    def __init__(self):
        self.conexion = Conexion()
    
    
    def agregar_compra(self, datos_compra, detalle_compra):
        """
        Registra una compra completa (cabecera + detalle + libro_compras + cuentas_por_pagar + stock)
        
        Parámetros:
        - datos_compra: dict con datos de la cabecera
        - detalle_compra: list de dict con productos
        
        Retorna:
        - id_compra si tiene éxito
        - None si hay error
        """
        try:
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            
            query_cabecera = """
            INSERT INTO compra (
                id_orden, id_proveedor, id_sucursal, id_empleado,
                nro_factura, timbrado, fecha_compra, fecha_vencimiento_timbrado,
                id_tipo_factura, cantidad_cuotas, saldo,
                id_estado_compra, observacion
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_compra
            """
            
            cursor.execute(query_cabecera, (
                datos_compra['id_orden'],
                datos_compra['id_proveedor'],
                datos_compra['id_sucursal'],
                datos_compra['id_empleado'],
                datos_compra['nro_factura'],
                datos_compra['timbrado'],
                datos_compra['fecha_compra'],
                datos_compra['fecha_vencimiento_timbrado'],
                datos_compra['id_tipo_factura'],
                datos_compra['cantidad_cuotas'],
                datos_compra['saldo'],
                1,  # Estado: Registrada
                datos_compra.get('observacion', None)
            ))
            
            id_compra = cursor.fetchone()[0]
            
            
            query_detalle = """
            INSERT INTO compra_detalle (
                id_compra, id_producto, id_impuesto, cantidad, precio_unitario
            ) VALUES (%s, %s, %s, %s, %s)
            """
            
            for item in detalle_compra:
                cursor.execute(query_detalle, (
                    id_compra,
                    item['id_producto'],
                    item['id_impuesto'],
                    item['cantidad'],
                    item['precio_unitario']
                ))
            
            
            query_totales = """
            SELECT subtotal, total_iva, total_compra, 
                   gravadas_10, iva_10, gravadas_5, iva_5, exentas
            FROM vista_compra_totales
            WHERE id_compra = %s
            """
            cursor.execute(query_totales, (id_compra,))
            totales = cursor.fetchone()
            
            
            query_libro = """
            INSERT INTO libro_compras (
                id_compra, id_proveedor, timbrado, nro_factura, fecha_factura,
                gravadas_10, iva_10, gravadas_5, iva_5, exentas, total_factura,
                periodo_mes, periodo_anio
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Extraer mes y año de la fecha de compra
            from datetime import datetime
            fecha_obj = datetime.strptime(datos_compra['fecha_compra'], '%Y-%m-%d')
            
            cursor.execute(query_libro, (
                id_compra,
                datos_compra['id_proveedor'],
                datos_compra['timbrado'],
                datos_compra['nro_factura'],
                datos_compra['fecha_compra'],
                totales[3],  # gravadas_10
                totales[4],  # iva_10
                totales[5],  # gravadas_5
                totales[6],  # iva_5
                totales[7],  # exentas
                totales[2],  # total_compra
                fecha_obj.month,
                fecha_obj.year
            ))
            
            
            if datos_compra['id_tipo_factura'] == 2:  # 2 = Crédito
                query_cuenta = """
                INSERT INTO cuentas_por_pagar (
                    id_compra, id_proveedor, nro_factura, saldo, 
                    fecha_vencimiento, id_estado_cuenta
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(query_cuenta, (
                    id_compra,
                    datos_compra['id_proveedor'],
                    datos_compra['nro_factura'],
                    datos_compra['saldo'],
                    datos_compra['fecha_vencimiento'],
                    1  # Estado: Pendiente
                ))
            
           
            for item in detalle_compra:
                # Verificar si existe el producto en el depósito
                query_check_stock = """
                SELECT id_stock, cantidad_actual 
                FROM stock 
                WHERE id_producto = %s AND id_deposito = %s
                """
                cursor.execute(query_check_stock, (
                    item['id_producto'],
                    datos_compra['id_deposito']
                ))
                stock_actual = cursor.fetchone()
                
                if stock_actual:
                    # Actualizar stock existente
                    query_update_stock = """
                    UPDATE stock 
                    SET cantidad_actual = cantidad_actual + %s
                    WHERE id_producto = %s AND id_deposito = %s
                    """
                    cursor.execute(query_update_stock, (
                        item['cantidad'],
                        item['id_producto'],
                        datos_compra['id_deposito']
                    ))
                else:
                    # Crear nuevo registro de stock
                    query_insert_stock = """
                    INSERT INTO stock (id_producto, id_deposito, cantidad_actual)
                    VALUES (%s, %s, %s)
                    """
                    cursor.execute(query_insert_stock, (
                        item['id_producto'],
                        datos_compra['id_deposito'],
                        item['cantidad']
                    ))
            
            
            query_update_orden = """
            UPDATE orden_de_compra
            SET id_estorden = 3
            WHERE id_orden = %s
            """
            cursor.execute(query_update_orden, (datos_compra['id_orden'],))
            
            con.commit()
            return id_compra
            
        except Exception as e:
            if con:
                con.rollback()
            print(f"Error en agregar_compra: {str(e)}")
            return None
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    def obtener_todas(self):
        """
        Obtiene todas las compras con información resumida
        """
        try:
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT 
                c.id_compra,
                c.nro_factura,
                c.fecha_compra,
                p.razon_social AS proveedor,
                s.descripcion AS sucursal,
                tf.descripcion AS tipo_factura,
                ec.descripcion AS estado,
                vct.total_compra,
                c.saldo
            FROM compra c
            INNER JOIN proveedores p ON c.id_proveedor = p.id_proveedor
            INNER JOIN sucursales s ON c.id_sucursal = s.id_sucursal
            INNER JOIN tipo_factura tf ON c.id_tipo_factura = tf.id_tipo_factura
            INNER JOIN estado_compra ec ON c.id_estado_compra = ec.id_estado_compra
            INNER JOIN vista_compra_totales vct ON c.id_compra = vct.id_compra
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
                    'sucursal': compra[4],
                    'tipo_factura': compra[5],
                    'estado': compra[6],
                    'total_compra': float(compra[7]) if compra[7] else 0,
                    'saldo': float(compra[8]) if compra[8] else 0
                })
            
            return lista_compras
            
        except Exception as e:
            print(f"Error en obtener_todas: {str(e)}")
            return []
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    def obtener_por_id(self, id_compra):
        """
        Obtiene una compra completa con su detalle
        """
        try:
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            # Obtener cabecera
            query_cabecera = """
            SELECT 
                c.id_compra,
                c.id_orden,
                c.id_proveedor,
                p.razon_social AS proveedor,
                c.id_sucursal,
                s.descripcion AS sucursal,
                c.id_empleado,
                CONCAT(pe.nombres, ' ', pe.apellidos) AS empleado,
                c.nro_factura,
                c.timbrado,
                c.fecha_compra,
                c.fecha_vencimiento_timbrado,
                c.id_tipo_factura,
                tf.descripcion AS tipo_factura,
                c.cantidad_cuotas,
                c.saldo,
                c.id_estado_compra,
                ec.descripcion AS estado,
                c.observacion,
                vct.subtotal,
                vct.total_iva,
                vct.total_compra
            FROM compra c
            INNER JOIN proveedores p ON c.id_proveedor = p.id_proveedor
            INNER JOIN sucursales s ON c.id_sucursal = s.id_sucursal
            INNER JOIN empleados e ON c.id_empleado = e.id_empleado
            INNER JOIN personas pe ON e.id_empleado = pe.id_persona
            INNER JOIN tipo_factura tf ON c.id_tipo_factura = tf.id_tipo_factura
            INNER JOIN estado_compra ec ON c.id_estado_compra = ec.id_estado_compra
            INNER JOIN vista_compra_totales vct ON c.id_compra = vct.id_compra
            WHERE c.id_compra = %s
            """
            
            cursor.execute(query_cabecera, (id_compra,))
            cabecera = cursor.fetchone()
            
            if not cabecera:
                return None
            
            # Obtener detalle
            query_detalle = """
            SELECT 
                cd.id_producto,
                pr.nombre AS producto,
                cd.cantidad,
                cd.precio_unitario,
                cd.id_impuesto,
                imp.descripcion AS impuesto,
                imp.tasa AS tasa_iva,
                (cd.cantidad * cd.precio_unitario) AS subtotal,
                (cd.cantidad * cd.precio_unitario * imp.tasa / 100) AS monto_iva,
                (cd.cantidad * cd.precio_unitario * (1 + imp.tasa / 100)) AS total
            FROM compra_detalle cd
            INNER JOIN productos pr ON cd.id_producto = pr.id_producto
            INNER JOIN impuestos imp ON cd.id_impuesto = imp.id_impuesto
            WHERE cd.id_compra = %s
            """
            
            cursor.execute(query_detalle, (id_compra,))
            detalle = cursor.fetchall()
            
            detalle_lista = []
            for item in detalle:
                detalle_lista.append({
                    'id_producto': item[0],
                    'producto': item[1],
                    'cantidad': item[2],
                    'precio_unitario': float(item[3]),
                    'id_impuesto': item[4],
                    'impuesto': item[5],
                    'tasa_iva': float(item[6]),
                    'subtotal': float(item[7]),
                    'monto_iva': float(item[8]),
                    'total': float(item[9])
                })
            
            return {
                'id_compra': cabecera[0],
                'id_orden': cabecera[1],
                'id_proveedor': cabecera[2],
                'proveedor': cabecera[3],
                'id_sucursal': cabecera[4],
                'sucursal': cabecera[5],
                'id_empleado': cabecera[6],
                'empleado': cabecera[7],
                'nro_factura': cabecera[8],
                'timbrado': cabecera[9],
                'fecha_compra': cabecera[10].strftime('%Y-%m-%d') if cabecera[10] else None,
                'fecha_vencimiento_timbrado': cabecera[11].strftime('%Y-%m-%d') if cabecera[11] else None,
                'id_tipo_factura': cabecera[12],
                'tipo_factura': cabecera[13],
                'cantidad_cuotas': cabecera[14],
                'saldo': float(cabecera[15]),
                'id_estado_compra': cabecera[16],
                'estado': cabecera[17],
                'observacion': cabecera[18],
                'subtotal': float(cabecera[19]),
                'total_iva': float(cabecera[20]),
                'total_compra': float(cabecera[21]),
                'detalle': detalle_lista
            }
            
        except Exception as e:
            print(f"Error en obtener_por_id: {str(e)}")
            return None
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    

    def anular_compra(self, id_compra):
        """
        Anula una compra (cambia estado a Anulada)
        """
        try:
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            UPDATE compra
            SET id_estado_compra = 3
            WHERE id_compra = %s AND id_estado_compra != 2
            """
            
            cursor.execute(query, (id_compra,))
            
            if cursor.rowcount > 0:
                con.commit()
                return True
            else:
                return False
            
        except Exception as e:
            if con:
                con.rollback()
            print(f"Error en anular_compra: {str(e)}")
            return False
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    

    def finalizar_compra(self, id_compra):
        """
        Cambia el estado de la compra a Finalizada
        """
        try:
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            UPDATE compra
            SET id_estado_compra = 2
            WHERE id_compra = %s AND id_estado_compra = 1
            """
            
            cursor.execute(query, (id_compra,))
            
            if cursor.rowcount > 0:
                con.commit()
                return True
            else:
                return False
            
        except Exception as e:
            if con:
                con.rollback()
            print(f"Error en finalizar_compra: {str(e)}")
            return False
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    def existe_compra_para_orden(self, id_orden):
        """
        Verifica si ya existe una compra registrada para una orden
        """
        try:
            con = self.conexion.getConexion()
            cursor = con.cursor()
            
            query = """
            SELECT COUNT(*) 
            FROM compra 
            WHERE id_orden = %s AND id_estado_compra != 3
            """
            
            cursor.execute(query, (id_orden,))
            resultado = cursor.fetchone()
            
            return resultado[0] > 0
            
        except Exception as e:
            print(f"Error en existe_compra_para_orden: {str(e)}")
            return False
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()