from flask import Blueprint, request, jsonify
from app.dao.gestionar_servicios.registrar_promociones.registrar_promociones_dao import PromocionDao

# Crear Blueprint
promocionapi = Blueprint('promocionapi', __name__)

# ========================================================================
# ENDPOINTS - PROMOCIONES
# ========================================================================

# ========== ENDPOINT 1: OBTENER TODAS LAS PROMOCIONES ==========
@promocionapi.route('/promociones', methods=['GET'])
def obtener_promociones():
    """
    GET /api/v1/gestionar-servicios/promocion/promociones
    Retorna todas las promociones registradas
    """
    try:
        dao = PromocionDao()
        promociones = dao.obtener_todas()
        
        return jsonify({
            'success': True,
            'data': promociones,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_promociones: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener promociones: {str(e)}'
        }), 500


# ========== ENDPOINT 2: OBTENER PROMOCIÓN POR ID ==========
@promocionapi.route('/promociones/<int:id_promocion>', methods=['GET'])
def obtener_promocion_por_id(id_promocion):
    """
    GET /api/v1/gestionar-servicios/promocion/promociones/<id>
    Retorna una promoción específica con su detalle
    """
    try:
        dao = PromocionDao()
        promocion = dao.obtener_por_id(id_promocion)
        
        if promocion:
            return jsonify({
                'success': True,
                'data': promocion,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró la promoción N° {id_promocion}'
            }), 404
            
    except Exception as e:
        print(f"❌ ERROR en obtener_promocion_por_id: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener la promoción: {str(e)}'
        }), 500


# ========== ENDPOINT 3: REGISTRAR NUEVA PROMOCIÓN ==========
@promocionapi.route('/promociones', methods=['POST'])
def registrar_promocion():
    """
    POST /api/v1/gestionar-servicios/promocion/promociones
    Registra una nueva promoción
    """
    try:
        print("========== DEBUG API: Iniciando registro de promoción ==========")
        
        data = request.get_json()
        print(f"DEBUG API: Data recibida: {data}")
        
        # Validar campos requeridos
        campos_requeridos = [
            'id_tipo_promocion', 'nombre_promocion',
            'fecha_inicio', 'fecha_fin', 'detalle_promocion'
        ]
        
        for campo in campos_requeridos:
            if campo not in data or data[campo] is None or data[campo] == '':
                return jsonify({
                    'success': False,
                    'error': f'El campo {campo} es obligatorio'
                }), 400
        
        # Validar fechas
        if data['fecha_inicio'] > data['fecha_fin']:
            return jsonify({
                'success': False,
                'error': 'La fecha de inicio no puede ser posterior a la fecha de fin'
            }), 400
        
        # Validar detalle
        if not isinstance(data['detalle_promocion'], list) or len(data['detalle_promocion']) == 0:
            return jsonify({
                'success': False,
                'error': 'Debe agregar al menos un producto a la promoción'
            }), 400
        
        # Validar estructura del detalle
        for item in data['detalle_promocion']:
            if 'id_producto' not in item or 'porcentaje_descuento' not in item:
                return jsonify({
                    'success': False,
                    'error': 'Cada producto debe tener id_producto y porcentaje_descuento'
                }), 400
            
            porcentaje = float(item['porcentaje_descuento'])
            if porcentaje <= 0 or porcentaje > 100:
                return jsonify({
                    'success': False,
                    'error': 'El porcentaje de descuento debe estar entre 1 y 100'
                }), 400
        
        # Preparar datos
        datos_promocion = {
            'id_tipo_promocion': data['id_tipo_promocion'],
            'nombre_promocion': data['nombre_promocion'],
            'descripcion': data.get('descripcion', None),
            'fecha_inicio': data['fecha_inicio'],
            'fecha_fin': data['fecha_fin']
        }
        
        # Registrar promoción
        dao = PromocionDao()
        id_promocion = dao.agregar_promocion(datos_promocion, data['detalle_promocion'])
        
        if id_promocion:
            print(f"DEBUG API: Promoción registrada exitosamente. ID: {id_promocion}")
            return jsonify({
                'success': True,
                'mensaje': f'Promoción N° {id_promocion} registrada exitosamente',
                'id_promocion': id_promocion
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo registrar la promoción'
            }), 500
            
    except ValueError as ve:
        print(f"❌ ERROR de validación: {str(ve)}")
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400
        
    except Exception as e:
        print(f"❌ ERROR en registrar_promocion: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Error al procesar la promoción: {str(e)}'
        }), 500


# ========== ENDPOINT 4: ACTIVAR/DESACTIVAR PROMOCIÓN ==========
@promocionapi.route('/promociones/<int:id_promocion>/estado', methods=['PUT'])
def cambiar_estado_promocion(id_promocion):
    """
    PUT /api/v1/gestionar-servicios/promocion/promociones/<id>/estado
    Activa o desactiva una promoción
    
    Body: { "activa": true/false }
    """
    try:
        print(f"========== DEBUG API: Cambiando estado de promoción {id_promocion} ==========")
        
        data = request.get_json()
        
        if 'activa' not in data:
            return jsonify({
                'success': False,
                'error': 'Debe especificar el estado (activa: true/false)'
            }), 400
        
        activa = data['activa']
        
        # Validar tipo de dato
        if not isinstance(activa, bool):
            return jsonify({
                'success': False,
                'error': 'El estado debe ser true o false'
            }), 400
        
        dao = PromocionDao()
        
        if dao.cambiar_estado(id_promocion, activa):
            estado_texto = 'activada' if activa else 'desactivada'
            
            print(f"DEBUG API: Promoción {estado_texto} exitosamente")
            return jsonify({
                'success': True,
                'mensaje': f'Promoción {estado_texto} exitosamente'
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
        print(f"❌ ERROR en cambiar_estado_promocion: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Error al cambiar el estado: {str(e)}'
        }), 500


# ========================================================================
# ENDPOINTS AUXILIARES
# ========================================================================

# ========== ENDPOINT 5: OBTENER TIPOS DE PROMOCIÓN ==========
@promocionapi.route('/tipos-promocion', methods=['GET'])
def obtener_tipos_promocion():
    """
    GET /api/v1/gestionar-servicios/promocion/tipos-promocion
    Retorna todos los tipos de promoción disponibles
    """
    try:
        dao = PromocionDao()
        tipos = dao.obtener_tipos_promocion()
        
        return jsonify({
            'success': True,
            'data': tipos,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_tipos_promocion: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener tipos de promoción: {str(e)}'
        }), 500


# ========== ENDPOINT 6: OBTENER PRODUCTOS ==========
@promocionapi.route('/productos', methods=['GET'])
def obtener_productos():
    """
    GET /api/v1/gestionar-servicios/promocion/productos
    Retorna todos los productos disponibles
    """
    try:
        dao = PromocionDao()
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