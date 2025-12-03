from flask import Blueprint, request, jsonify
from app.dao.gestionar_servicios.registrar_presupuesto_servicio.registrar_presupuesto_servicio_dao import PresupuestoServicioDao
import re

# Crear Blueprint
presupuestoapi = Blueprint('presupuestoapi', __name__)

# ========================================================================
# ENDPOINTS - PRESUPUESTOS DE SERVICIO
# ========================================================================

# ========== ENDPOINT 1: OBTENER TODOS LOS PRESUPUESTOS ==========
@presupuestoapi.route('/presupuestos', methods=['GET'])
def obtener_presupuestos():
    """
    GET /api/v1/gestionar-servicios/presupuesto-servicio/presupuestos
    Retorna todos los presupuestos de servicio registrados
    """
    try:
        dao = PresupuestoServicioDao()
        presupuestos = dao.obtener_todos()
        
        return jsonify({
            'success': True,
            'data': presupuestos,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_presupuestos: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener presupuestos: {str(e)}'
        }), 500


# ========== ENDPOINT 2: OBTENER PRESUPUESTO POR ID ==========
@presupuestoapi.route('/presupuestos/<int:id_presupuesto>', methods=['GET'])
def obtener_presupuesto_por_id(id_presupuesto):
    """
    GET /api/v1/gestionar-servicios/presupuesto-servicio/presupuestos/<id>
    Retorna un presupuesto específico con su detalle y totales
    """
    try:
        dao = PresupuestoServicioDao()
        presupuesto = dao.obtener_por_id(id_presupuesto)
        
        if presupuesto:
            return jsonify({
                'success': True,
                'data': presupuesto,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró el presupuesto N° {id_presupuesto}'
            }), 404
            
    except Exception as e:
        print(f"❌ ERROR en obtener_presupuesto_por_id: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener el presupuesto: {str(e)}'
        }), 500


# ========== ENDPOINT 3: REGISTRAR NUEVO PRESUPUESTO ==========
@presupuestoapi.route('/presupuestos', methods=['POST'])
def registrar_presupuesto():
    """
    POST /api/v1/gestionar-servicios/presupuesto-servicio/presupuestos
    Registra un nuevo presupuesto de servicio
    """
    try:
        print("========== DEBUG API: Iniciando registro de presupuesto ==========")
        
        data = request.get_json()
        print(f"DEBUG API: Data recibida: {data}")
        
        # Validar campos requeridos
        campos_requeridos = [
            'id_solicitud', 'id_cliente', 'id_empleado',
            'nro_presupuesto', 'fecha_presupuesto', 'fecha_validez',
            'detalle_presupuesto'
        ]
        
        for campo in campos_requeridos:
            if campo not in data or data[campo] is None or data[campo] == '':
                return jsonify({
                    'success': False,
                    'error': f'El campo {campo} es obligatorio'
                }), 400
        
        # Validar formato del número de presupuesto (ejemplo: PSERV-2025-001)
        if not re.match(r'^[A-Z]+-\d{4}-\d{3,6}$', data['nro_presupuesto']):
            return jsonify({
                'success': False,
                'error': 'El formato del número de presupuesto debe ser PSERV-YYYY-XXX (ej: PSERV-2025-001)'
            }), 400
        
        # Validar detalle
        if not isinstance(data['detalle_presupuesto'], list) or len(data['detalle_presupuesto']) == 0:
            return jsonify({
                'success': False,
                'error': 'Debe agregar al menos un producto/servicio al presupuesto'
            }), 400
        
        # Validar estructura del detalle
        for item in data['detalle_presupuesto']:
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
        datos_presupuesto = {
            'id_solicitud': data['id_solicitud'],
            'id_cliente': data['id_cliente'],
            'id_empleado': data['id_empleado'],
            'nro_presupuesto': data['nro_presupuesto'],
            'fecha_presupuesto': data['fecha_presupuesto'],
            'fecha_validez': data['fecha_validez'],
            'observaciones': data.get('observaciones', None)
        }
        
        # Registrar presupuesto
        dao = PresupuestoServicioDao()
        id_presupuesto = dao.agregar_presupuesto(datos_presupuesto, data['detalle_presupuesto'])
        
        if id_presupuesto:
            print(f"DEBUG API: Presupuesto registrado exitosamente. ID: {id_presupuesto}")
            return jsonify({
                'success': True,
                'mensaje': f'Presupuesto N° {id_presupuesto} registrado exitosamente',
                'id_presupuesto': id_presupuesto
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo registrar el presupuesto'
            }), 500
            
    except ValueError as ve:
        print(f"❌ ERROR de validación: {str(ve)}")
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400
        
    except Exception as e:
        print(f"❌ ERROR en registrar_presupuesto: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Error al procesar el presupuesto: {str(e)}'
        }), 500


# ========== ENDPOINT 4: CAMBIAR ESTADO DE PRESUPUESTO ==========
@presupuestoapi.route('/presupuestos/<int:id_presupuesto>/estado', methods=['PUT'])
def cambiar_estado_presupuesto(id_presupuesto):
    """
    PUT /api/v1/gestionar-servicios/presupuesto-servicio/presupuestos/<id>/estado
    Cambia el estado de un presupuesto
    
    Body: { "id_estado": 2 }
    Estados:
    1 = Pendiente
    2 = Aprobado
    3 = Rechazado
    4 = Anulado
    """
    try:
        print(f"========== DEBUG API: Cambiando estado de presupuesto {id_presupuesto} ==========")
        
        data = request.get_json()
        
        if 'id_estado' not in data:
            return jsonify({
                'success': False,
                'error': 'Debe especificar el id_estado'
            }), 400
        
        id_estado_nuevo = data['id_estado']
        
        # Validar estado válido
        if id_estado_nuevo not in [1, 2, 3, 4]:
            return jsonify({
                'success': False,
                'error': 'Estado inválido. Debe ser 1 (Pendiente), 2 (Aprobado), 3 (Rechazado) o 4 (Anulado)'
            }), 400
        
        dao = PresupuestoServicioDao()
        
        if dao.cambiar_estado(id_presupuesto, id_estado_nuevo):
            estados_dict = {
                1: 'Pendiente',
                2: 'Aprobado',
                3: 'Rechazado',
                4: 'Anulado'
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
        print(f"❌ ERROR en cambiar_estado_presupuesto: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Error al cambiar el estado: {str(e)}'
        }), 500


# ========================================================================
# ENDPOINTS AUXILIARES
# ========================================================================

# ========== ENDPOINT 5: OBTENER SOLICITUDES FINALIZADAS ==========
@presupuestoapi.route('/solicitudes-disponibles', methods=['GET'])
def obtener_solicitudes_disponibles():
    """
    GET /api/v1/gestionar-servicios/presupuesto-servicio/solicitudes-disponibles
    Retorna solicitudes finalizadas disponibles para presupuestar
    """
    try:
        dao = PresupuestoServicioDao()
        solicitudes = dao.obtener_solicitudes_finalizadas()
        
        return jsonify({
            'success': True,
            'data': solicitudes,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_solicitudes_disponibles: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener solicitudes: {str(e)}'
        }), 500


# ========== ENDPOINT 6: OBTENER PRODUCTOS DE SOLICITUD ==========
@presupuestoapi.route('/solicitudes/<int:id_solicitud>/productos', methods=['GET'])
def obtener_productos_solicitud(id_solicitud):
    """
    GET /api/v1/gestionar-servicios/presupuesto-servicio/solicitudes/<id>/productos
    Retorna los productos de una solicitud específica
    """
    try:
        dao = PresupuestoServicioDao()
        productos = dao.obtener_productos_solicitud(id_solicitud)
        
        return jsonify({
            'success': True,
            'data': productos,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_productos_solicitud: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener productos: {str(e)}'
        }), 500


# ========== ENDPOINT 7: OBTENER IMPUESTOS ==========
@presupuestoapi.route('/impuestos', methods=['GET'])
def obtener_impuestos():
    """
    GET /api/v1/gestionar-servicios/presupuesto-servicio/impuestos
    Retorna todos los impuestos disponibles
    """
    try:
        dao = PresupuestoServicioDao()
        impuestos = dao.obtener_impuestos()
        
        return jsonify({
            'success': True,
            'data': impuestos,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_impuestos: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener impuestos: {str(e)}'
        }), 500