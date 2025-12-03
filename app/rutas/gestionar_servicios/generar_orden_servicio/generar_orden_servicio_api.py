from flask import Blueprint, request, jsonify
from app.dao.gestionar_servicios.generar_orden_servicio.generar_orden_servicio_dao import OrdenServicioDao
import re

# Crear Blueprint
ordenapi = Blueprint('ordenapi', __name__)

# ========================================================================
# ENDPOINTS - ÓRDENES DE SERVICIO
# ========================================================================

# ========== ENDPOINT 1: OBTENER TODAS LAS ÓRDENES ==========
@ordenapi.route('/ordenes', methods=['GET'])
def obtener_ordenes():
    """
    GET /api/v1/gestionar-servicios/orden-servicio/ordenes
    Retorna todas las órdenes de servicio registradas
    """
    try:
        dao = OrdenServicioDao()
        ordenes = dao.obtener_todas()
        
        return jsonify({
            'success': True,
            'data': ordenes,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_ordenes: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener órdenes: {str(e)}'
        }), 500


# ========== ENDPOINT 2: OBTENER ORDEN POR ID ==========
@ordenapi.route('/ordenes/<int:id_orden_servicio>', methods=['GET'])
def obtener_orden_por_id(id_orden_servicio):
    """
    GET /api/v1/gestionar-servicios/orden-servicio/ordenes/<id>
    Retorna una orden específica con su detalle y totales
    """
    try:
        dao = OrdenServicioDao()
        orden = dao.obtener_por_id(id_orden_servicio)
        
        if orden:
            return jsonify({
                'success': True,
                'data': orden,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró la orden N° {id_orden_servicio}'
            }), 404
            
    except Exception as e:
        print(f"❌ ERROR en obtener_orden_por_id: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener la orden: {str(e)}'
        }), 500


# ========== ENDPOINT 3: REGISTRAR NUEVA ORDEN ==========
@ordenapi.route('/ordenes', methods=['POST'])
def registrar_orden():
    """
    POST /api/v1/gestionar-servicios/orden-servicio/ordenes
    Registra una nueva orden de servicio
    """
    try:
        print("========== DEBUG API: Iniciando registro de orden ==========")
        
        data = request.get_json()
        print(f"DEBUG API: Data recibida: {data}")
        
        # Validar campos requeridos
        campos_requeridos = [
            'id_presupuesto', 'id_cliente', 'id_empleado',
            'nro_orden_servicio', 'fecha_orden', 'fecha_inicio_estimada',
            'fecha_fin_estimada', 'detalle_orden'
        ]
        
        for campo in campos_requeridos:
            if campo not in data or data[campo] is None or data[campo] == '':
                return jsonify({
                    'success': False,
                    'error': f'El campo {campo} es obligatorio'
                }), 400
        
        # Validar formato del número de orden (ejemplo: OSERV-2025-001)
        if not re.match(r'^[A-Z]+-\d{4}-\d{3,6}$', data['nro_orden_servicio']):
            return jsonify({
                'success': False,
                'error': 'El formato del número de orden debe ser OSERV-YYYY-XXX (ej: OSERV-2025-001)'
            }), 400
        
        # Validar detalle
        if not isinstance(data['detalle_orden'], list) or len(data['detalle_orden']) == 0:
            return jsonify({
                'success': False,
                'error': 'Debe agregar al menos un producto/servicio a la orden'
            }), 400
        
        # Validar estructura del detalle
        for item in data['detalle_orden']:
            if 'id_producto' not in item or 'cantidad' not in item or 'precio_unitario' not in item or 'id_impuesto' not in item:
                return jsonify({
                    'success': False,
                    'error': 'Cada producto debe tener id_producto, cantidad, precio_unitario e id_impuesto'
                }), 400
            
            if item['cantidad'] <= 0:
                return jsonify({
                    'success': False,
                    'error': 'La cantidad debe ser mayor a 0'
                }), 400
            
            if item['precio_unitario'] < 0:
                return jsonify({
                    'success': False,
                    'error': 'El precio unitario no puede ser negativo'
                }), 400
        
        # Preparar datos
        datos_orden = {
            'id_presupuesto': data['id_presupuesto'],
            'id_cliente': data['id_cliente'],
            'id_empleado': data['id_empleado'],
            'nro_orden_servicio': data['nro_orden_servicio'],
            'fecha_orden': data['fecha_orden'],
            'fecha_inicio_estimada': data['fecha_inicio_estimada'],
            'fecha_fin_estimada': data['fecha_fin_estimada'],
            'observaciones': data.get('observaciones', None)
        }
        
        # Registrar orden
        dao = OrdenServicioDao()
        id_orden_servicio = dao.agregar_orden(datos_orden, data['detalle_orden'])
        
        if id_orden_servicio:
            print(f"DEBUG API: Orden registrada exitosamente. ID: {id_orden_servicio}")
            return jsonify({
                'success': True,
                'mensaje': f'Orden N° {id_orden_servicio} registrada exitosamente',
                'id_orden_servicio': id_orden_servicio
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo registrar la orden'
            }), 500
            
    except ValueError as ve:
        print(f"❌ ERROR de validación: {str(ve)}")
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400
        
    except Exception as e:
        print(f"❌ ERROR en registrar_orden: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Error al procesar la orden: {str(e)}'
        }), 500


# ========== ENDPOINT 4: CAMBIAR ESTADO DE ORDEN ==========
@ordenapi.route('/ordenes/<int:id_orden_servicio>/estado', methods=['PUT'])
def cambiar_estado_orden(id_orden_servicio):
    """
    PUT /api/v1/gestionar-servicios/orden-servicio/ordenes/<id>/estado
    Cambia el estado de una orden
    
    Body: { "id_estado": 2 }
    Estados:
    1 = Borrador
    2 = Autorizada
    3 = Anulada
    """
    try:
        print(f"========== DEBUG API: Cambiando estado de orden {id_orden_servicio} ==========")
        
        data = request.get_json()
        
        if 'id_estado' not in data:
            return jsonify({
                'success': False,
                'error': 'Debe especificar el id_estado'
            }), 400
        
        id_estado_nuevo = data['id_estado']
        
        # Validar estado válido
        if id_estado_nuevo not in [1, 2, 3]:
            return jsonify({
                'success': False,
                'error': 'Estado inválido. Debe ser 1 (Borrador), 2 (Autorizada) o 3 (Anulada)'
            }), 400
        
        dao = OrdenServicioDao()
        
        if dao.cambiar_estado(id_orden_servicio, id_estado_nuevo):
            estados_dict = {
                1: 'Borrador',
                2: 'Autorizada',
                3: 'Anulada'
            }
            
            print(f"DEBUG API: Estado cambiado exitosamente a {estados_dict[id_estado_nuevo]}")
            return jsonify({
                'success': True,
                'mensaje': f'Estado cambiado a {estados_dict[id_estado_nuevo]}'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo cambiar el estado'
            }), 500
            
    except ValueError as ve:
        print(f"❌ ERROR de validación: {str(ve)}")
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400
        
    except Exception as e:
        print(f"❌ ERROR en cambiar_estado_orden: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Error al cambiar el estado: {str(e)}'
        }), 500


# ========================================================================
# ENDPOINTS AUXILIARES
# ========================================================================

# ========== ENDPOINT 5: OBTENER PRESUPUESTOS APROBADOS ==========
@ordenapi.route('/presupuestos-disponibles', methods=['GET'])
def obtener_presupuestos_disponibles():
    """
    GET /api/v1/gestionar-servicios/orden-servicio/presupuestos-disponibles
    Retorna presupuestos aprobados disponibles para generar orden
    """
    try:
        dao = OrdenServicioDao()
        presupuestos = dao.obtener_presupuestos_aprobados()
        
        return jsonify({
            'success': True,
            'data': presupuestos,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_presupuestos_disponibles: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener presupuestos: {str(e)}'
        }), 500


# ========== ENDPOINT 6: OBTENER PRODUCTOS DE PRESUPUESTO ==========
@ordenapi.route('/presupuestos/<int:id_presupuesto>/productos', methods=['GET'])
def obtener_productos_presupuesto(id_presupuesto):
    """
    GET /api/v1/gestionar-servicios/orden-servicio/presupuestos/<id>/productos
    Retorna los productos de un presupuesto específico
    """
    try:
        dao = OrdenServicioDao()
        productos = dao.obtener_productos_presupuesto(id_presupuesto)
        
        return jsonify({
            'success': True,
            'data': productos,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_productos_presupuesto: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener productos: {str(e)}'
        }), 500