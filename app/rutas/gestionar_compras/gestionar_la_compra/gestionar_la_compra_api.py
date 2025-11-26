from flask import Blueprint, request, jsonify
from app.dao.gestionar_compras.gestionar_la_compra.gestionar_la_compra_dao import CompraDao

# Crear Blueprint
compraapi = Blueprint('compraapi', __name__)

# Diccionario de estados
ESTADOS_COMPRA = {
    'registrada': 1,
    'finalizada': 2,
    'anulada': 3
}

# ENDPOINT 1: OBTENER TODAS LAS COMPRAS
@compraapi.route('/compras', methods=['GET'])
def obtener_compras():
    """
    GET /api/v1/gestionar-compras/gestionar-compra/compras
    Retorna todas las compras registradas
    """
    try:
        dao = CompraDao()
        compras = dao.obtener_todas()
        
        return jsonify({
            'success': True,
            'data': compras,
            'error': None
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al obtener compras: {str(e)}'
        }), 500


# ENDPOINT 2: OBTENER COMPRA POR ID
@compraapi.route('/compras/<int:id_compra>', methods=['GET'])
def obtener_compra_por_id(id_compra):
    """
    GET /api/v1/gestionar-compras/gestionar-compra/compras/<id>
    Retorna una compra específica con su detalle
    """
    try:
        dao = CompraDao()
        compra = dao.obtener_por_id(id_compra)
        
        if compra:
            return jsonify({
                'success': True,
                'data': compra,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró la compra N° {id_compra}'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al obtener la compra: {str(e)}'
        }), 500


# ENDPOINT 3: REGISTRAR NUEVA COMPRA
@compraapi.route('/compras', methods=['POST'])
def registrar_compra():
    """
    POST /api/v1/gestionar-compras/gestionar-compra/compras
    Registra una nueva compra
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        campos_requeridos = [
            'id_orden', 'id_proveedor', 'id_sucursal', 'id_empleado', 'id_deposito',
            'nro_factura', 'timbrado', 'fecha_compra', 'fecha_vencimiento_timbrado',
            'id_tipo_factura', 'detalle_compra'
        ]
        
        for campo in campos_requeridos:
            if campo not in data or data[campo] is None:
                return jsonify({
                    'success': False,
                    'error': f'El campo {campo} es obligatorio'
                }), 400
        
        # Validar que detalle_compra no esté vacío
        if not isinstance(data['detalle_compra'], list) or len(data['detalle_compra']) == 0:
            return jsonify({
                'success': False,
                'error': 'El detalle de la compra debe contener al menos un producto'
            }), 400
        
        # Validar estructura de cada producto
        for item in data['detalle_compra']:
            if 'id_producto' not in item or 'id_impuesto' not in item or 'cantidad' not in item or 'precio_unitario' not in item:
                return jsonify({
                    'success': False,
                    'error': 'Cada producto debe tener id_producto, id_impuesto, cantidad y precio_unitario'
                }), 400
        
        # Validar formato de número de factura (XXX-XXX-XXXXXXX)
        import re
        if not re.match(r'^\d{3}-\d{3}-\d{7}$', data['nro_factura']):
            return jsonify({
                'success': False,
                'error': 'El número de factura debe tener el formato XXX-XXX-XXXXXXX'
            }), 400
        
        # Validar formato de timbrado (8 dígitos)
        if not re.match(r'^\d{8}$', data['timbrado']):
            return jsonify({
                'success': False,
                'error': 'El timbrado debe tener 8 dígitos numéricos'
            }), 400
        
        # Validar tipo de factura
        if data['id_tipo_factura'] not in [1, 2]:
            return jsonify({
                'success': False,
                'error': 'El tipo de factura debe ser 1 (Contado) o 2 (Crédito)'
            }), 400
        
        # Si es crédito, validar campos adicionales
        if data['id_tipo_factura'] == 2:
            if 'cantidad_cuotas' not in data or data['cantidad_cuotas'] < 1:
                return jsonify({
                    'success': False,
                    'error': 'Para crédito, la cantidad de cuotas debe ser al menos 1'
                }), 400
            
            if 'saldo' not in data or data['saldo'] <= 0:
                return jsonify({
                    'success': False,
                    'error': 'Para crédito, el saldo debe ser mayor a 0'
                }), 400
            
            if 'fecha_vencimiento' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Para crédito, la fecha de vencimiento es obligatoria'
                }), 400
        else:
            # Si es contado, forzar valores
            data['cantidad_cuotas'] = 1
            data['saldo'] = 0
        
        # Validar que la orden no tenga ya una compra registrada
        dao = CompraDao()
        if dao.existe_compra_para_orden(data['id_orden']):
            return jsonify({
                'success': False,
                'error': f'La Orden N° {data["id_orden"]} ya tiene una compra registrada'
            }), 400
        
        # Preparar datos de cabecera
        datos_compra = {
            'id_orden': data['id_orden'],
            'id_proveedor': data['id_proveedor'],
            'id_sucursal': data['id_sucursal'],
            'id_empleado': data['id_empleado'],
            'id_deposito': data['id_deposito'],
            'nro_factura': data['nro_factura'],
            'timbrado': data['timbrado'],
            'fecha_compra': data['fecha_compra'],
            'fecha_vencimiento_timbrado': data['fecha_vencimiento_timbrado'],
            'id_tipo_factura': data['id_tipo_factura'],
            'cantidad_cuotas': data.get('cantidad_cuotas', 1),
            'saldo': data.get('saldo', 0),
            'observacion': data.get('observacion', None)
        }
        
        # Si es crédito, agregar fecha de vencimiento
        if data['id_tipo_factura'] == 2:
            datos_compra['fecha_vencimiento'] = data['fecha_vencimiento']
        
        # Registrar la compra
        id_compra = dao.agregar_compra(datos_compra, data['detalle_compra'])
        
        if id_compra:
            return jsonify({
                'success': True,
                'mensaje': f'Compra N° {id_compra} registrada exitosamente',
                'id_compra': id_compra
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo registrar la compra. Consulte con el administrador'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al procesar la solicitud: {str(e)}'
        }), 500


# ENDPOINT 4: ANULAR COMPRA
@compraapi.route('/compras/<int:id_compra>/anular', methods=['PUT'])
def anular_compra(id_compra):
    """
    PUT /api/v1/gestionar-compras/gestionar-compra/compras/<id>/anular
    Anula una compra
    """
    try:
        dao = CompraDao()
        
        # Verificar que la compra existe
        compra = dao.obtener_por_id(id_compra)
        if not compra:
            return jsonify({
                'success': False,
                'error': f'No se encontró la compra N° {id_compra}'
            }), 404
        
        # Verificar que no esté finalizada
        if compra['id_estado_compra'] == 2:
            return jsonify({
                'success': False,
                'error': 'No se puede anular una compra finalizada'
            }), 400
        
        # Verificar que no esté ya anulada
        if compra['id_estado_compra'] == 3:
            return jsonify({
                'success': False,
                'error': 'Esta compra ya está anulada'
            }), 400
        
        # Anular
        if dao.anular_compra(id_compra):
            return jsonify({
                'success': True,
                'mensaje': f'Compra N° {id_compra} anulada exitosamente'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo anular la compra'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al anular la compra: {str(e)}'
        }), 500


# ENDPOINT 5: FINALIZAR COMPRA
@compraapi.route('/compras/<int:id_compra>/finalizar', methods=['PUT'])
def finalizar_compra(id_compra):
    """
    PUT /api/v1/gestionar-compras/gestionar-compra/compras/<id>/finalizar
    Finaliza una compra (cambia estado a Finalizada)
    """
    try:
        dao = CompraDao()
        
        # Verificar que la compra existe
        compra = dao.obtener_por_id(id_compra)
        if not compra:
            return jsonify({
                'success': False,
                'error': f'No se encontró la compra N° {id_compra}'
            }), 404
        
        # Verificar que esté en estado Registrada
        if compra['id_estado_compra'] != 1:
            return jsonify({
                'success': False,
                'error': 'Solo se pueden finalizar compras en estado Registrada'
            }), 400
        
        # Finalizar
        if dao.finalizar_compra(id_compra):
            return jsonify({
                'success': True,
                'mensaje': f'Compra N° {id_compra} finalizada exitosamente'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo finalizar la compra'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al finalizar la compra: {str(e)}'
        }), 500



# ENDPOINT 6: OBTENER ÓRDENES DISPONIBLES (Estado Aprobada)

@compraapi.route('/ordenes-disponibles', methods=['GET'])
def obtener_ordenes_disponibles():
    """
    GET /api/v1/gestionar-compras/gestionar-compra/ordenes-disponibles
    Retorna las órdenes de compra en estado "Aprobada" que no tienen compra registrada
    """
    try:
        dao = CompraDao()
        con = dao.conexion.getConexion()
        cursor = con.cursor()
        
        query = """
        SELECT 
            oc.id_orden,
            oc.id_presupuesto,
            oc.fecha_orden,
            p.razon_social AS proveedor,
            s.descripcion AS sucursal
        FROM orden_de_compra oc
        INNER JOIN presupuesto_prov pp ON oc.id_presupuesto = pp.id_presupuesto
        INNER JOIN proveedores p ON pp.id_proveedor = p.id_proveedor
        INNER JOIN sucursales s ON oc.id_sucursal = s.id_sucursal
        WHERE oc.id_estorden = 2  -- Estado: Aprobada
        AND NOT EXISTS (
            SELECT 1 FROM compra c 
            WHERE c.id_orden = oc.id_orden 
            AND c.id_estado_compra != 3  -- Excluir anuladas
        )
        ORDER BY oc.fecha_orden DESC
        """
        
        cursor.execute(query)
        ordenes = cursor.fetchall()
        
        lista_ordenes = []
        for orden in ordenes:
            lista_ordenes.append({
                'id_orden': orden[0],
                'id_presupuesto': orden[1],
                'fecha_orden': orden[2].strftime('%Y-%m-%d') if orden[2] else None,
                'proveedor': orden[3],
                'sucursal': orden[4]
            })
        
        cursor.close()
        con.close()
        
        return jsonify({
            'success': True,
            'data': lista_ordenes,
            'error': None
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al obtener órdenes: {str(e)}'
        }), 500



# ENDPOINT 7: OBTENER DETALLE DE ORDEN (para cargar productos)

@compraapi.route('/orden-detalle/<int:id_orden>', methods=['GET'])
def obtener_orden_detalle(id_orden):
    """
    GET /api/v1/gestionar-compras/gestionar-compra/orden-detalle/<id>
    Retorna el detalle de productos de una orden
    """
    try:
        dao = CompraDao()
        con = dao.conexion.getConexion()
        cursor = con.cursor()
        
        # Obtener info de la orden
        query_orden = """
        SELECT 
            oc.id_orden,
            oc.id_presupuesto,
            oc.id_sucursal,
            pp.id_proveedor,
            p.razon_social AS proveedor,
            s.descripcion AS sucursal
        FROM orden_de_compra oc
        INNER JOIN presupuesto_prov pp ON oc.id_presupuesto = pp.id_presupuesto
        INNER JOIN proveedores p ON pp.id_proveedor = p.id_proveedor
        INNER JOIN sucursales s ON oc.id_sucursal = s.id_sucursal
        WHERE oc.id_orden = %s
        """
        
        cursor.execute(query_orden, (id_orden,))
        orden = cursor.fetchone()
        
        if not orden:
            cursor.close()
            con.close()
            return jsonify({
                'success': False,
                'error': 'Orden no encontrada'
            }), 404
        
        # Obtener productos
        query_productos = """
        SELECT 
            ocd.id_producto,
            pr.nombre AS producto,
            ocd.cantidad,
            ocd.precio
        FROM orden_de_compra_detalle ocd
        INNER JOIN productos pr ON ocd.id_producto = pr.id_producto
        WHERE ocd.id_orden = %s
        """
        
        cursor.execute(query_productos, (id_orden,))
        productos = cursor.fetchall()
        
        detalle_productos = []
        for prod in productos:
            detalle_productos.append({
                'id_producto': prod[0],
                'nombre': prod[1],
                'cantidad': prod[2],
                'precio': float(prod[3])
            })
        
        cursor.close()
        con.close()
        
        return jsonify({
            'success': True,
            'data': {
                'id_orden': orden[0],
                'id_presupuesto': orden[1],
                'id_sucursal': orden[2],
                'id_proveedor': orden[3],
                'proveedor': orden[4],
                'sucursal': orden[5],
                'productos': detalle_productos
            },
            'error': None
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al obtener detalle: {str(e)}'
        }), 500


# ENDPOINT 8: OBTENER DEPÓSITOS DE UNA SUCURSAL

@compraapi.route('/depositos/<int:id_sucursal>', methods=['GET'])
def obtener_depositos(id_sucursal):
    """
    GET /api/v1/gestionar-compras/gestionar-compra/depositos/<id_sucursal>
    Retorna los depósitos de una sucursal
    """
    try:
        dao = CompraDao()
        con = dao.conexion.getConexion()
        cursor = con.cursor()
        
        query = """
        SELECT id_deposito, descripcion
        FROM depositos
        WHERE id_sucursal = %s
        ORDER BY descripcion
        """
        
        cursor.execute(query, (id_sucursal,))
        depositos = cursor.fetchall()
        
        lista_depositos = []
        for dep in depositos:
            lista_depositos.append({
                'id_deposito': dep[0],
                'descripcion': dep[1]
            })
        
        cursor.close()
        con.close()
        
        return jsonify({
            'success': True,
            'data': lista_depositos,
            'error': None
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al obtener depósitos: {str(e)}'
        }), 500