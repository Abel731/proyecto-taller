from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.sucursal.SurcursalDao import SucursalDao

sucapi = Blueprint('sucapi', __name__)

@sucapi.route('/sucursal-depositos/<int:id_sucursal>', methods=['GET'])
def get_sucursal_depositos(id_sucursal):
    dao = SucursalDao()

    try:
        pedidos = dao.get_sucursal_depositos(id_sucursal)
        return jsonify({
            'success': True,
            'data': pedidos,
            'error': False
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener los pedidos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador'
        }), 500

@sucapi.route('/sucursales', methods=['GET'])
def getSucursales():
    sucursaldao = SucursalDao()

    try:
        sucursales = sucursaldao.getSucursales()

        return jsonify({
            'success': True,
            'data': sucursales,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todas las sucursales : {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@sucapi.route('/sucursales/<int:id_sucursal>', methods=['GET'])
def getSucursal(id_sucursal):
    sucursaldao = SucursalDao()

    try:
        sucursal = sucursaldao.getSucursalById(id_sucursal)

        if sucursal:
            return jsonify({
                'success': True,
                'data': sucursal,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la sucursal con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener sucursal: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@sucapi.route('/sucursales', methods=['POST'])
def addSucursal():
    data = request.get_json()
    sucursaldao = SucursalDao()

    campos_requeridos = ['descripcion']

    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or len(data[campo].strip()) == 0:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    try:
        id_sucursal = sucursaldao.guardarSucursal(
            data['descripcion'].strip().upper(),
        )
        
        return jsonify({
            'success': True,
            'data': {
                'id_sucursal': id_sucursal,
                'descripcion': data['descripcion'].upper(),
            },
            'error': None
        }), 201

    except Exception as e:
        app.logger.error(f"Error al agregar sucursal: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@sucapi.route('/sucursales/<int:id_sucursal>', methods=['PUT'])
def updateSucursal(id_sucursal):
    data = request.get_json()
    sucursaldao = SucursalDao()

    campos_requeridos = ['descripcion']

    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or len(data[campo].strip()) == 0:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    try:
        if sucursaldao.updateSucursal(
            id_sucursal,
            data['descripcion'].strip().upper(),
        ):
            return jsonify({
                'success': True,
                'data': {
                    'id_sucursal': id_sucursal,
                    'descripcion': data['descripcion'].upper(),
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la sucursal con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar sucursal: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@sucapi.route('/sucursales/<int:id_sucursal>', methods=['DELETE'])
def deleteSucursal(id_sucursal):
    sucursaldao = SucursalDao()

    try:
        if sucursaldao.deleteSucursal(id_sucursal):
            return jsonify({
                'success': True,
                'mensaje': f'Sucursal con ID {id_sucursal} eliminada correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la sucursal con el ID proporcionado o no se pudo eliminar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar sucursal: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
