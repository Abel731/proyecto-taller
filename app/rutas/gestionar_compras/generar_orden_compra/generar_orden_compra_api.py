from datetime import date
from flask import Blueprint, jsonify, request, current_app as app
from app.dao.gestionar_compras.generar_orden_compra.orden_compra_dao import OrdenCompraDao

ocapi = Blueprint('ocapi', __name__)

# Mapeo de estados
ESTADOS_ORDEN = {
    'pendiente': 1,
    'aprobada': 2,
    'procesada': 3,
    'cancelada': 4
}

# Obtener todas las órdenes de compra
@ocapi.route('/ordenes', methods=['GET'])
def get_ordenes():
    dao = OrdenCompraDao()

    try:
        ordenes = dao.obtener_ordenes()
        return jsonify({
            'success': True,
            'data': ordenes,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener las órdenes: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Obtener información del presupuesto (sucursal, proveedor, empleado)
@ocapi.route('/info-presupuesto/<int:id_presupuesto>', methods=['GET'])
def get_info_presupuesto(id_presupuesto):
    dao = OrdenCompraDao()
    
    try:
        info = dao.get_info_presupuesto(id_presupuesto)
        if info:
            return jsonify({
                'success': True,
                'data': info,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró información del presupuesto.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener info del presupuesto: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Obtener detalle de productos del presupuesto
@ocapi.route('/detalle-presupuesto/<int:id_presupuesto>', methods=['GET'])
def get_detalle_presupuesto(id_presupuesto):
    dao = OrdenCompraDao()
    
    try:
        detalle = dao.get_detalle_presupuesto(id_presupuesto)
        if detalle:
            return jsonify({
                'success': True,
                'data': detalle,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontraron productos para este presupuesto.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener el detalle del presupuesto: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Crear nueva orden de compra
@ocapi.route('/ordenes', methods=['POST'])
def add_orden():
    ocdao = OrdenCompraDao()
    data = request.get_json()

    # Validar campos requeridos
    campos_requeridos = ['id_presupuesto', 'id_empleado', 'id_sucursal', 'fecha_orden', 'detalle_orden', 'estado']
    
    for campo in campos_requeridos:
        if campo not in data or data[campo] is None:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    # Validar que detalle_orden no esté vacío
    if not isinstance(data['detalle_orden'], list) or len(data['detalle_orden']) == 0:
        return jsonify({
            'success': False,
            'error': 'El detalle de la orden debe contener al menos un producto.'
        }), 400

    # Validar estructura de cada detalle
    for item in data['detalle_orden']:
        if 'id_producto' not in item or 'cantidad' not in item or 'precio' not in item:
            return jsonify({
                'success': False,
                'error': 'Cada producto debe tener id_producto, cantidad y precio.'
            }), 400

    
    id_presupuesto = data['id_presupuesto']
    
    if ocdao.existe_orden_activa_para_presupuesto(id_presupuesto):
        return jsonify({
            'success': False,
            'error': f'Ya existe una orden de compra activa para el Presupuesto N° {id_presupuesto}. No se pueden generar órdenes duplicadas del mismo presupuesto.'
        }), 400
    

    try:
        id_empleado = data['id_empleado']
        id_sucursal = data['id_sucursal']
        fecha_orden = data['fecha_orden']
        detalle_orden = data['detalle_orden']
        estado = data['estado']

        # Verificar que el estado es válido
        if estado not in ESTADOS_ORDEN:
            return jsonify({
                'success': False,
                'error': f'El estado {estado} no es válido.'
            }), 400

        # Crear la orden con el estado seleccionado
        resultado = ocdao.agregar(
            id_presupuesto=id_presupuesto,
            id_empleado=id_empleado,
            id_sucursal=id_sucursal,
            id_estorden=ESTADOS_ORDEN[estado],
            fecha_orden=fecha_orden,
            detalle_orden=detalle_orden
        )

        if resultado:
            return jsonify({
                'success': True,
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo crear la orden de compra. Consulte con el administrador.'
            }), 500

    except Exception as e:
        app.logger.error(f"Error al crear orden de compra: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Anular orden de compra
@ocapi.route('/ordenes/<int:id_orden>/anular', methods=['PUT'])
def anular_orden(id_orden):
    dao = OrdenCompraDao()

    try:
        resultado = dao.anular(id_orden)
        
        if resultado:
            return jsonify({
                'success': True,
                'mensaje': f'Orden N° {id_orden} anulada correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la orden o no se pudo anular.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al anular orden: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
    
# Obtener una orden específica por ID
@ocapi.route('/ordenes/<int:id_orden>', methods=['GET'])
def get_orden_by_id(id_orden):
    dao = OrdenCompraDao()
    
    try:
        orden = dao.get_orden_por_id(id_orden)
        
        if orden:
            return jsonify({
                'success': True,
                'data': orden,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró la orden N° {id_orden}.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener orden {id_orden}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Actualizar estado de una orden
@ocapi.route('/ordenes/<int:id_orden>/estado', methods=['PUT'])
def actualizar_estado_orden(id_orden):
    dao = OrdenCompraDao()
    data = request.get_json()

    # Validar que venga el campo estado
    if 'estado' not in data or data['estado'] is None:
        return jsonify({
            'success': False,
            'error': 'El campo estado es obligatorio.'
        }), 400

    try:
        estado = data['estado']

        # Verificar que el estado es válido
        if estado not in ESTADOS_ORDEN:
            return jsonify({
                'success': False,
                'error': f'El estado "{estado}" no es válido. Estados permitidos: {list(ESTADOS_ORDEN.keys())}'
            }), 400

        # Obtener la orden actual para validar transiciones
        orden_actual = dao.get_orden_por_id(id_orden)
        
        if not orden_actual:
            return jsonify({
                'success': False,
                'error': f'No se encontró la orden N° {id_orden}.'
            }), 404

        # Validar transiciones de estado
        estado_actual = orden_actual['estado'].lower()
        estado_nuevo = estado.lower()

        # Reglas de transición
        transiciones_validas = {
            'pendiente': ['aprobada', 'cancelada'],
            'aprobada': ['procesada', 'cancelada'],
            'procesada': [],  # No puede cambiar
            'cancelada': []   # No puede cambiar
        }

        if estado_nuevo not in transiciones_validas.get(estado_actual, []):
            estados_permitidos = transiciones_validas.get(estado_actual, [])
            if not estados_permitidos:
                return jsonify({
                    'success': False,
                    'error': f'Una orden en estado "{orden_actual["estado"]}" no puede cambiar de estado.'
                }), 400
            else:
                return jsonify({
                    'success': False,
                    'error': f'No se puede cambiar de "{orden_actual["estado"]}" a "{estado.capitalize()}". Estados permitidos: {[e.capitalize() for e in estados_permitidos]}'
                }), 400

        # Actualizar el estado
        id_estorden_nuevo = ESTADOS_ORDEN[estado]
        resultado = dao.actualizar_estado(id_orden, id_estorden_nuevo)

        if resultado:
            return jsonify({
                'success': True,
                'mensaje': f'Estado de la orden N° {id_orden} actualizado a "{estado.capitalize()}".',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo actualizar el estado de la orden.'
            }), 500

    except Exception as e:
        app.logger.error(f"Error al actualizar estado de orden {id_orden}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500    