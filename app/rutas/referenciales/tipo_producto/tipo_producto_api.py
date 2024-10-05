from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.tipo_producto.Tipo_ProductoDao import Tipo_ProductoDao

tipo_producto_api = Blueprint('tipo_producto_api', __name__)

# Trae todos los tipos de producto
@tipo_producto_api.route('/tipo_productos', methods=['GET'])
def getTipoProductos():
    tipo_producto_dao = Tipo_ProductoDao()

    try:
        tipo_productos = tipo_producto_dao.getTipoProductos()

        return jsonify({
            'success': True,
            'data': tipo_productos,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todos los tipos de producto: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@tipo_producto_api.route('/tipo_productos/<int:tipo_producto_id>', methods=['GET'])
def getTipoProducto(tipo_producto_id):
    tipo_producto_dao = Tipo_ProductoDao()

    try:
        tipo_producto = tipo_producto_dao.getTipoProductoById(tipo_producto_id)

        if tipo_producto:
            return jsonify({
                'success': True,
                'data': tipo_producto,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el tipo de producto con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener tipo de producto: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Agrega un nuevo tipo de producto
@tipo_producto_api.route('/tipo_productos', methods=['POST'])
def addTipoProducto():
    data = request.get_json()
    tipo_producto_dao = Tipo_ProductoDao()

    # Validar que el JSON no esté vacío y tenga las propiedades necesarias
    campos_requeridos = ['descripcion']

    # Verificar si faltan campos o son vacíos
    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or len(data[campo].strip()) == 0:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    try:
        descripcion = data['descripcion'].upper()
        tipo_producto_id = tipo_producto_dao.guardarTipoProducto(descripcion)
        if tipo_producto_id is not None:
            return jsonify({
                'success': True,
                'data': {'id': tipo_producto_id, 'descripcion': descripcion},
                'error': None
            }), 201
        else:
            return jsonify({'success': False, 'error': 'No se pudo guardar el tipo de producto. Consulte con el administrador.'}), 500
    except Exception as e:
        app.logger.error(f"Error al agregar tipo de producto: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@tipo_producto_api.route('/tipo_productos/<int:tipo_producto_id>', methods=['PUT'])
def updateTipoProducto(tipo_producto_id):
    data = request.get_json()
    tipo_producto_dao = Tipo_ProductoDao()

    # Validar que el JSON no esté vacío y tenga las propiedades necesarias
    campos_requeridos = ['descripcion']

    # Verificar si faltan campos o son vacíos
    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or len(data[campo].strip()) == 0:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    descripcion = data['descripcion']
    
    try:
        if tipo_producto_dao.updateTipoProducto(tipo_producto_id, descripcion.upper()):
            return jsonify({
                'success': True,
                'data': {'id': tipo_producto_id, 'descripcion': descripcion},
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el tipo de producto con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar tipo de producto: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@tipo_producto_api.route('/tipo_productos/<int:tipo_producto_id>', methods=['DELETE'])
def deleteTipoProducto(tipo_producto_id):
    tipo_producto_dao = Tipo_ProductoDao()

    try:
        # Usar el retorno de eliminarTipoProducto para determinar el éxito
        if tipo_producto_dao.deleteTipoProducto(tipo_producto_id):
            return jsonify({
                'success': True,
                'mensaje': f'Tipo de producto con ID {tipo_producto_id} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el tipo de producto con el ID proporcionado o no se pudo eliminar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar tipo de producto: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
