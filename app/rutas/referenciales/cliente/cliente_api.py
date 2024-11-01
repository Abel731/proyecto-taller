from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.cliente.ClienteDao import ClienteDao

cliapi = Blueprint('cliapi', __name__)

@cliapi.route('/clientes', methods=['GET'])
def getClientes():
    clientedao = ClienteDao()

    try:
        clientes = clientedao.getClientes()

        return jsonify({
            'success': True,
            'data': clientes,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todos los clientes: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@cliapi.route('/clientes/<int:id_cliente>', methods=['GET'])
def getCliente(id_cliente):
    clientedao = ClienteDao()

    try:
        cliente = clientedao.getClienteById(id_cliente)

        if cliente:
            return jsonify({
                'success': True,
                'data': cliente,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el cliente con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener cliente: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@cliapi.route('/clientes', methods=['POST'])
def addCliente():
    data = request.get_json()
    clientedao = ClienteDao()

    campos_requeridos = ['direccion', 'telefono']
    print("Datos recibidos:", data)  # Para verificar los datos recibidos
    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or len(data[campo].strip()) == 0:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    try:
        # Asegúrate de que id_cliente sea un entero
        id_cliente = int(data['cliente'])  # Convierte a entero
        id_guardado = clientedao.guardarCliente(
            id_cliente,  # Pasa id_cliente aquí
            data['direccion'].strip().upper(),  # Dirección
            data['telefono']  # Teléfono
        )

        return jsonify({
            'success': True,
            'data': {
                'id_cliente': id_guardado,  # Devuelve el ID guardado
                'direccion': data['direccion'].upper(),
                'telefono': data['telefono']
            },
            'error': None
        }), 201

    except Exception as e:
        app.logger.error(f"Error al agregar cliente: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
    
@cliapi.route('/clientes/<int:id_cliente>', methods=['PUT'])
def updateCliente(id_cliente):
    data = request.get_json()

     # Imprime el contenido de data para depuración
    print("Cliente data:", data)  # Esta línea imprime el contenido de data

    clientedao = ClienteDao()

    campos_requeridos = ['direccion', 'telefono']

    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or len(data[campo].strip()) == 0:
            return jsonify({
                            'success': False,
                            'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
                            }), 400
    direccion = data['direccion']
    telefono = data['telefono']
    try:
        if clientedao.updateCliente(id_cliente, direccion.upper(),telefono):
            return jsonify({
                'success': True,
                'data': {'id': id_cliente, 'direccion': direccion, 'telefono': telefono},
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el cliente con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar cliente: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
    
@cliapi.route('/clientes/<int:id_cliente>', methods=['DELETE'])
def deleteCliente(id_cliente):
    clientedao = ClienteDao()

    try:
        if clientedao.deleteCliente(id_cliente):
            return jsonify({
                'success': True,
                'mensaje': f'Cliente con ID {id_cliente} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el cliente con el ID proporcionado o no se pudo eliminar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar cliente: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
