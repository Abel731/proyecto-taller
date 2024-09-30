from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.proveedor.ProveedorDao import ProveedorDao

provapi = Blueprint('provapi', __name__)

@provapi.route('/proveedores', methods=['GET'])
def getProveedores():
    proveedordao = ProveedorDao()

    try:
        proveedores = proveedordao.getProveedores()

        return jsonify({
            'success': True,
            'data': proveedores,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todos los proveedores: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@provapi.route('/proveedores/<int:id_proveedor>', methods=['GET'])
def getProveedor(id_proveedor):
    proveedordao = ProveedorDao()

    try:
        proveedor = proveedordao.getProveedorById(id_proveedor)

        if proveedor:
            return jsonify({
                'success': True,
                'data': proveedor,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el proveedor con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener proveedor: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@provapi.route('/proveedores', methods=['POST'])
def addProveedor():
    data = request.get_json()
    proveedordao = ProveedorDao()

    campos_requeridos = ['ruc', 'razon_social', 'registro', 'estado']

    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or len(data[campo].strip()) == 0:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

  
    estado = data['estado'].lower()
    if estado not in ['activo', 'inactivo', 'pendiente']:
        return jsonify({
            'success': False,
            'error': 'El estado debe ser "activo", "inactivo" o "pendiente".'
        }), 400

    try:
        id_proveedor = proveedordao.guardarProveedor(
            data['ruc'].strip(),
            data['razon_social'].strip().upper(),
            data['registro'],
            estado 
        )

        return jsonify({
            'success': True,
            'data': {
                'id_proveedor': id_proveedor,
                'ruc': data['ruc'].strip(),
                'razon_social': data['razon_social'].upper(),
                'registro': data['registro'],
                'estado': estado  
            },
            'error': None
        }), 201

    except Exception as e:
        app.logger.error(f"Error al agregar proveedor: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@provapi.route('/proveedores/<int:id_proveedor>', methods=['PUT'])
def updateProveedor(id_proveedor):
    data = request.get_json()
    proveedordao = ProveedorDao()

    campos_requeridos = ['ruc', 'razon_social', 'registro', 'estado']

    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or len(data[campo].strip()) == 0:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    # Validar y normalizar el estado
    estado = data['estado'].lower()
    if estado not in ['activo', 'inactivo', 'pendiente']:
        return jsonify({
            'success': False,
            'error': 'El estado debe ser "activo", "inactivo" o "pendiente".'
        }), 400

    try:
        if proveedordao.updateProveedor(
            id_proveedor,
            data['ruc'].strip(),
            data['razon_social'].strip().upper(),
            data['registro'],
            estado  # Usar estado como string
        ):
            return jsonify({
                'success': True,
                'data': {
                    'id_proveedor': id_proveedor,
                    'ruc': data['ruc'].strip(),
                    'razon_social': data['razon_social'].upper(),
                    'registro': data['registro'],
                    'estado': estado  # Devolver estado como string
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el proveedor con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar proveedor: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@provapi.route('/proveedores/<int:id_proveedor>', methods=['DELETE'])
def deleteProveedor(id_proveedor):
    proveedordao = ProveedorDao()

    try:
        if proveedordao.deleteProveedor(id_proveedor):
            return jsonify({
                'success': True,
                'mensaje': f'Proveedor con ID {id_proveedor} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el proveedor con el ID proporcionado o no se pudo eliminar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar proveedor: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
