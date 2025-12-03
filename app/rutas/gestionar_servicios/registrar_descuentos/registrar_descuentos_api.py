from flask import Blueprint, request, jsonify
from app.dao.gestionar_servicios.registrar_descuentos.registrar_descuentos_dao import DescuentoDao

# Crear Blueprint
descuentoapi = Blueprint('descuentoapi', __name__)

# ========================================================================
# ENDPOINTS - DESCUENTOS
# ========================================================================

# ========== ENDPOINT 1: OBTENER TODOS LOS DESCUENTOS ==========
@descuentoapi.route('/descuentos', methods=['GET'])
def obtener_descuentos():
    """
    GET /api/v1/gestionar-servicios/descuento/descuentos
    Retorna todos los descuentos registrados
    """
    try:
        dao = DescuentoDao()
        descuentos = dao.obtener_todos()
        
        return jsonify({
            'success': True,
            'data': descuentos,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_descuentos: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener descuentos: {str(e)}'
        }), 500


# ========== ENDPOINT 2: OBTENER DESCUENTO POR ID ==========
@descuentoapi.route('/descuentos/<int:id_descuento>', methods=['GET'])
def obtener_descuento_por_id(id_descuento):
    """
    GET /api/v1/gestionar-servicios/descuento/descuentos/<id>
    Retorna un descuento específico con su detalle
    """
    try:
        dao = DescuentoDao()
        descuento = dao.obtener_por_id(id_descuento)
        
        if descuento:
            return jsonify({
                'success': True,
                'data': descuento,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró el descuento N° {id_descuento}'
            }), 404
            
    except Exception as e:
        print(f"❌ ERROR en obtener_descuento_por_id: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener el descuento: {str(e)}'
        }), 500


# ========== ENDPOINT 3: REGISTRAR NUEVO DESCUENTO ==========
@descuentoapi.route('/descuentos', methods=['POST'])
def registrar_descuento():
    """
    POST /api/v1/gestionar-servicios/descuento/descuentos
    Registra un nuevo descuento
    """
    try:
        print("========== DEBUG API: Iniciando registro de descuento ==========")
        
        data = request.get_json()
        print(f"DEBUG API: Data recibida: {data}")
        
        # Validar campos requeridos
        campos_requeridos = [
            'id_tipo_descuento', 'nombre_descuento',
            'fecha_inicio', 'detalle_descuento'
        ]
        
        for campo in campos_requeridos:
            if campo not in data or data[campo] is None or data[campo] == '':
                return jsonify({
                    'success': False,
                    'error': f'El campo {campo} es obligatorio'
                }), 400
        
        # Validar fechas (si fecha_fin existe)
        if data.get('fecha_fin') and data['fecha_inicio'] > data['fecha_fin']:
            return jsonify({
                'success': False,
                'error': 'La fecha de inicio no puede ser posterior a la fecha de fin'
            }), 400
        
        # Validar detalle
        if not isinstance(data['detalle_descuento'], list) or len(data['detalle_descuento']) == 0:
            return jsonify({
                'success': False,
                'error': 'Debe agregar al menos un producto al descuento'
            }), 400
        
        # Validar estructura del detalle
        for item in data['detalle_descuento']:
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
        datos_descuento = {
            'id_tipo_descuento': data['id_tipo_descuento'],
            'nombre_descuento': data['nombre_descuento'],
            'descripcion': data.get('descripcion', None),
            'fecha_inicio': data['fecha_inicio'],
            'fecha_fin': data.get('fecha_fin', None)  # Puede ser NULL para descuentos permanentes
        }
        
        # Registrar descuento
        dao = DescuentoDao()
        id_descuento = dao.agregar_descuento(datos_descuento, data['detalle_descuento'])
        
        if id_descuento:
            print(f"DEBUG API: Descuento registrado exitosamente. ID: {id_descuento}")
            return jsonify({
                'success': True,
                'mensaje': f'Descuento N° {id_descuento} registrado exitosamente',
                'id_descuento': id_descuento
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo registrar el descuento'
            }), 500
            
    except ValueError as ve:
        print(f"❌ ERROR de validación: {str(ve)}")
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400
        
    except Exception as e:
        print(f"❌ ERROR en registrar_descuento: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Error al procesar el descuento: {str(e)}'
        }), 500


# ========== ENDPOINT 4: ACTIVAR/DESACTIVAR DESCUENTO ==========
@descuentoapi.route('/descuentos/<int:id_descuento>/estado', methods=['PUT'])
def cambiar_estado_descuento(id_descuento):
    """
    PUT /api/v1/gestionar-servicios/descuento/descuentos/<id>/estado
    Activa o desactiva un descuento
    
    Body: { "activo": true/false }
    """
    try:
        print(f"========== DEBUG API: Cambiando estado de descuento {id_descuento} ==========")
        
        data = request.get_json()
        
        if 'activo' not in data:
            return jsonify({
                'success': False,
                'error': 'Debe especificar el estado (activo: true/false)'
            }), 400
        
        activo = data['activo']
        
        # Validar tipo de dato
        if not isinstance(activo, bool):
            return jsonify({
                'success': False,
                'error': 'El estado debe ser true o false'
            }), 400
        
        dao = DescuentoDao()
        
        if dao.cambiar_estado(id_descuento, activo):
            estado_texto = 'activado' if activo else 'desactivado'
            
            print(f"DEBUG API: Descuento {estado_texto} exitosamente")
            return jsonify({
                'success': True,
                'mensaje': f'Descuento {estado_texto} exitosamente'
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
        print(f"❌ ERROR en cambiar_estado_descuento: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Error al cambiar el estado: {str(e)}'
        }), 500


# ========================================================================
# ENDPOINTS AUXILIARES
# ========================================================================

# ========== ENDPOINT 5: OBTENER TIPOS DE DESCUENTO ==========
@descuentoapi.route('/tipos-descuento', methods=['GET'])
def obtener_tipos_descuento():
    """
    GET /api/v1/gestionar-servicios/descuento/tipos-descuento
    Retorna todos los tipos de descuento disponibles
    """
    try:
        dao = DescuentoDao()
        tipos = dao.obtener_tipos_descuento()
        
        return jsonify({
            'success': True,
            'data': tipos,
            'error': None
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR en obtener_tipos_descuento: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener tipos de descuento: {str(e)}'
        }), 500


# ========== ENDPOINT 6: OBTENER PRODUCTOS ==========
@descuentoapi.route('/productos', methods=['GET'])
def obtener_productos():
    """
    GET /api/v1/gestionar-servicios/descuento/productos
    Retorna todos los productos disponibles
    """
    try:
        dao = DescuentoDao()
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