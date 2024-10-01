from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.deposito.DepositoDao import DepositoDao

depoapi = Blueprint('depoapi', __name__)

@depoapi.route('/depositos', methods=['GET'])
def getDepositos():
    depositodao = DepositoDao()

    try:
        depositos = depositodao.getDepositos()

        return jsonify({
            'success': True,
            'data': depositos,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todos los depósitos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@depoapi.route('/depositos/<int:id_deposito>', methods=['GET'])
def getDeposito(id_deposito):
    depositodao = DepositoDao()

    try:
        deposito = depositodao.getDepositoById(id_deposito)

        if deposito:
            return jsonify({
                'success': True,
                'data': deposito,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el depósito con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener depósito: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@depoapi.route('/depositos', methods=['POST'])
def addDeposito():
    data = request.get_json()
    depositodao = DepositoDao()

    campos_requeridos = ['nombre', 'direccion', 'telefono', 'capacidad']

    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or len(data[campo].strip()) == 0:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    try:
        id_deposito = depositodao.guardarDeposito(
            data['nombre'].strip().upper(),
            data['direccion'].strip().upper(),
            data['telefono'],
            data['capacidad']
        )
        
        return jsonify({
            'success': True,
            'data': {
                'id_deposito': id_deposito,
                'nombre': data['nombre'].upper(),
                'direccion': data['direccion'].upper(),
                'telefono': data['telefono'],
                'capacidad': data['capacidad']
            },
            'error': None
        }), 201

    except Exception as e:
        app.logger.error(f"Error al agregar depósito: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@depoapi.route('/depositos/<int:id_deposito>', methods=['PUT'])
def updateDeposito(id_deposito):
    data = request.get_json()
    depositodao = DepositoDao()

    campos_requeridos = ['nombre', 'direccion', 'telefono', 'capacidad']

    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or len(data[campo].strip()) == 0:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    try:
        if depositodao.updateDeposito(
            id_deposito,
            data['nombre'].strip().upper(),
            data['direccion'].strip().upper(),
            data['telefono'],
            data['capacidad']
        ):
            return jsonify({
                'success': True,
                'data': {
                    'id_deposito': id_deposito,
                    'nombre': data['nombre'].upper(),
                    'direccion': data['direccion'].upper(),
                    'telefono': data['telefono'],
                    'capacidad': data['capacidad']
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el depósito con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar depósito: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@depoapi.route('/depositos/<int:id_deposito>', methods=['DELETE'])
def deleteDeposito(id_deposito):
    depositodao = DepositoDao()

    try:
        if depositodao.deleteDeposito(id_deposito):
            return jsonify({
                'success': True,
                'mensaje': f'Depósito con ID {id_deposito} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el depósito con el ID proporcionado o no se pudo eliminar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar depósito: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
