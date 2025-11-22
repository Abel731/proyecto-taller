from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.producto.ProductoDao import ProductoDao

proapi = Blueprint('proapi', __name__)

# Trae todos los productos
@proapi.route('/productos', methods=['GET'])
def getProductos():
    prodao = ProductoDao()

    try:
        productos = prodao.get_productos()

        return jsonify({
            'success': True,
            'data': productos,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todos los productos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@proapi.route('/productos/<int:producto_id>', methods=['GET'])
def getProducto(producto_id):
    prodao = ProductoDao()

    try:
        producto = prodao.getProductoById(producto_id)

        if producto:
            return jsonify({
                'success': True,
                'data': producto,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el producto con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener producto: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Agrega un nuevo producto
@proapi.route('/productos', methods=['POST'])
def addProducto():
    data = request.get_json()
    prodao = ProductoDao()

    # Validar que el JSON no esté vacío y tenga las propiedades necesarias
    campos_requeridos = ['nombre', 'precio_compra']

    # Verificar si faltan campos o son vacíos
    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or len(str(data[campo]).strip()) == 0:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    try:
        nombre = data['nombre'].upper()
        precio_compra = data['precio_compra']
        
        producto_guardado = prodao.guardarProducto(nombre, precio_compra)
        if producto_guardado:
            return jsonify({
                'success': True,
                'data': {'nombre': nombre, 'precio_compra': precio_compra},
                'error': None
            }), 201
        else:
            return jsonify({ 
                'success': False, 
                'error': 'No se pudo guardar el producto. Consulte con el administrador.' 
            }), 500
    except Exception as e:
        app.logger.error(f"Error al agregar producto: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@proapi.route('/productos/<int:producto_id>', methods=['PUT'])
def updateProducto(producto_id):
    data = request.get_json()
    prodao = ProductoDao()

    # Validar que el JSON no esté vacío y tenga las propiedades necesarias
    campos_requeridos = ['nombre', 'precio_compra']

    # Verificar si faltan campos o son vacíos
    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or len(str(data[campo]).strip()) == 0:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    nombre = data['nombre']
    precio_compra = data['precio_compra']
    
    try:
        if prodao.updateProducto(producto_id, nombre.upper(), precio_compra):
            return jsonify({
                'success': True,
                'data': {'id': producto_id, 'nombre': nombre, 'precio_compra': precio_compra},
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el producto con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar producto: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@proapi.route('/productos/<int:producto_id>', methods=['DELETE'])
def deleteProducto(producto_id):
    prodao = ProductoDao()

    try:
        if prodao.deleteProducto(producto_id):
            return jsonify({
                'success': True,
                'mensaje': f'Producto con ID {producto_id} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el producto con el ID proporcionado o no se pudo eliminar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar producto: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500