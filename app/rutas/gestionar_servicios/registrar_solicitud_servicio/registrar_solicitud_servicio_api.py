from flask import Blueprint, request, jsonify
from app.dao.gestionar_servicios.registrar_solicitud_servicio.registrar_solicitud_servicio_dao import SolicitudServicioDao

# Crear Blueprint
solicitudapi = Blueprint('solicitudapi', __name__)

# ========================================================================
# ENDPOINTS - SOLICITUDES DE SERVICIO
# ========================================================================

# ========== ENDPOINT 1: OBTENER TODAS LAS SOLICITUDES ==========
@solicitudapi.route('/solicitudes', methods=['GET'])
def obtener_solicitudes():
    """
    GET /api/v1/gestionar-servicios/solicitud-servicio/solicitudes
    Retorna todas las solicitudes de servicio registradas
    """
    try:
        dao = SolicitudServicioDao()
        solicitudes = dao.obtener_todas()
        
        return jsonify({
            'success': True,
            'data': solicitudes,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_solicitudes: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener solicitudes: {str(e)}'
        }), 500


# ========== ENDPOINT 2: OBTENER SOLICITUD POR ID ==========
@solicitudapi.route('/solicitudes/<int:id_solicitud>', methods=['GET'])
def obtener_solicitud_por_id(id_solicitud):
    """
    GET /api/v1/gestionar-servicios/solicitud-servicio/solicitudes/<id>
    Retorna una solicitud específica con su detalle
    """
    try:
        dao = SolicitudServicioDao()
        solicitud = dao.obtener_por_id(id_solicitud)
        
        if solicitud:
            return jsonify({
                'success': True,
                'data': solicitud,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró la solicitud N° {id_solicitud}'
            }), 404
            
    except Exception as e:
        print(f"❌ ERROR en obtener_solicitud_por_id: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener la solicitud: {str(e)}'
        }), 500


# ========== ENDPOINT 3: REGISTRAR NUEVA SOLICITUD ==========
@solicitudapi.route('/solicitudes', methods=['POST'])
def registrar_solicitud():
    """
    POST /api/v1/gestionar-servicios/solicitud-servicio/solicitudes
    Registra una nueva solicitud de servicio
    """
    try:
        print("========== DEBUG API: Iniciando registro de solicitud ==========")
        
        data = request.get_json()
        print(f"DEBUG API: Data recibida: {data}")
        
        # Validar campos requeridos
        campos_requeridos = [
            'id_cliente', 'id_tipo_servicio', 'id_empleado',
            'fecha_solicitud', 'hora_solicitud', 'descripcion_problema'
        ]
        
        for campo in campos_requeridos:
            if campo not in data or data[campo] is None or data[campo] == '':
                return jsonify({
                    'success': False,
                    'error': f'El campo {campo} es obligatorio'
                }), 400
        
        # Validar detalle (puede ser vacío)
        if 'detalle_solicitud' not in data:
            data['detalle_solicitud'] = []
        
        # Si hay detalle, validar estructura
        if len(data['detalle_solicitud']) > 0:
            for item in data['detalle_solicitud']:
                if 'id_producto' not in item or 'cantidad' not in item:
                    return jsonify({
                        'success': False,
                        'error': 'Cada producto debe tener id_producto y cantidad'
                    }), 400
                
                if item['cantidad'] <= 0:
                    return jsonify({
                        'success': False,
                        'error': 'La cantidad debe ser mayor a 0'
                    }), 400
        
        # Preparar datos
        datos_solicitud = {
            'id_cliente': data['id_cliente'],
            'id_tipo_servicio': data['id_tipo_servicio'],
            'id_empleado': data['id_empleado'],
            'fecha_solicitud': data['fecha_solicitud'],
            'hora_solicitud': data['hora_solicitud'],
            'descripcion_problema': data['descripcion_problema'],
            'observaciones': data.get('observaciones', None)
        }
        
        # Registrar solicitud
        dao = SolicitudServicioDao()
        id_solicitud = dao.agregar_solicitud(datos_solicitud, data['detalle_solicitud'])
        
        if id_solicitud:
            print(f"DEBUG API: Solicitud registrada exitosamente. ID: {id_solicitud}")
            return jsonify({
                'success': True,
                'mensaje': f'Solicitud N° {id_solicitud} registrada exitosamente',
                'id_solicitud': id_solicitud
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo registrar la solicitud'
            }), 500
            
    except Exception as e:
        print(f"❌ ERROR en registrar_solicitud: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Error al procesar la solicitud: {str(e)}'
        }), 500


# ========== ENDPOINT 4: CAMBIAR ESTADO DE SOLICITUD ==========
@solicitudapi.route('/solicitudes/<int:id_solicitud>/estado', methods=['PUT'])
def cambiar_estado_solicitud(id_solicitud):
    """
    PUT /api/v1/gestionar-servicios/solicitud-servicio/solicitudes/<id>/estado
    Cambia el estado de una solicitud
    
    Body: { "id_estado": 2 }
    Estados:
    1 = Pendiente
    2 = En Proceso
    3 = Finalizada
    4 = Anulada
    """
    try:
        print(f"========== DEBUG API: Cambiando estado de solicitud {id_solicitud} ==========")
        
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
                'error': 'Estado inválido. Debe ser 1 (Pendiente), 2 (En Proceso), 3 (Finalizada) o 4 (Anulada)'
            }), 400
        
        dao = SolicitudServicioDao()
        
        if dao.cambiar_estado(id_solicitud, id_estado_nuevo):
            estados_dict = {
                1: 'Pendiente',
                2: 'En Proceso',
                3: 'Finalizada',
                4: 'Anulada'
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
        print(f"❌ ERROR en cambiar_estado_solicitud: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Error al cambiar el estado: {str(e)}'
        }), 500


# ========================================================================
# ENDPOINTS AUXILIARES
# ========================================================================

# ========== ENDPOINT 5: OBTENER CLIENTES ==========
@solicitudapi.route('/clientes', methods=['GET'])
def obtener_clientes():
    """
    GET /api/v1/gestionar-servicios/solicitud-servicio/clientes
    Retorna todos los clientes activos
    """
    try:
        dao = SolicitudServicioDao()
        clientes = dao.obtener_clientes()
        
        return jsonify({
            'success': True,
            'data': clientes,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_clientes: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener clientes: {str(e)}'
        }), 500


# ========== ENDPOINT 6: OBTENER TIPOS DE SERVICIO ==========
@solicitudapi.route('/tipos-servicio', methods=['GET'])
def obtener_tipos_servicio():
    """
    GET /api/v1/gestionar-servicios/solicitud-servicio/tipos-servicio
    Retorna todos los tipos de servicio disponibles
    """
    try:
        dao = SolicitudServicioDao()
        tipos = dao.obtener_tipos_servicio()
        
        return jsonify({
            'success': True,
            'data': tipos,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_tipos_servicio: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener tipos de servicio: {str(e)}'
        }), 500


# ========== ENDPOINT 7: OBTENER PRODUCTOS ==========
@solicitudapi.route('/productos', methods=['GET'])
def obtener_productos():
    """
    GET /api/v1/gestionar-servicios/solicitud-servicio/productos
    Retorna todos los productos disponibles
    """
    try:
        dao = SolicitudServicioDao()
        productos = dao.obtener_productos()
        
        return jsonify({
            'success': True,
            'data': productos,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_productos: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener productos: {str(e)}'
        }), 500