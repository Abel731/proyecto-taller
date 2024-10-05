from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.emisora.EmisoraDao import EmisoraDao

emisoraapi = Blueprint('emisoraapi', __name__)

# Trae todas las emisoras
@emisoraapi.route('/emisoras', methods=['GET'])
def getEmisoras():
    emisorao = EmisoraDao()

    try:
        emisoras = emisorao.getEmisoras()

        return jsonify({
            'success': True,
            'data': emisoras,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todas las emisoras: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@emisoraapi.route('/emisoras/<int:emisora_id>', methods=['GET'])
def getEmisora(emisora_id):
    emisorao = EmisoraDao()

    try:
        emisora = emisorao.getEmisoraById(emisora_id)

        if emisora:
            return jsonify({
                'success': True,
                'data': emisora,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la emisora con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener emisora: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Agrega una nueva emisora
@emisoraapi.route('/emisoras', methods=['POST'])
def addEmisora():
    data = request.get_json()
    emisorao = EmisoraDao()

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
        emisora_id = emisorao.guardarEmisora(descripcion)
        if emisora_id is not None:
            return jsonify({
                'success': True,
                'data': {'id': emisora_id, 'descripcion': descripcion},
                'error': None
            }), 201
        else:
            return jsonify({'success': False, 'error': 'No se pudo guardar la emisora. Consulte con el administrador.'}), 500
    except Exception as e:
        app.logger.error(f"Error al agregar emisora: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@emisoraapi.route('/emisoras/<int:emisora_id>', methods=['PUT'])
def updateEmisora(emisora_id):
    data = request.get_json()
    emisorao = EmisoraDao()

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
        if emisorao.updateEmisora(emisora_id, descripcion.upper()):
            return jsonify({
                'success': True,
                'data': {'id': emisora_id, 'descripcion': descripcion},
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la emisora con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar emisora: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@emisoraapi.route('/emisoras/<int:emisora_id>', methods=['DELETE'])
def deleteEmisora(emisora_id):
    emisorao = EmisoraDao()

    try:
        # Usar el retorno de eliminarEmisora para determinar el éxito
        if emisorao.deleteEmisora(emisora_id):
            return jsonify({
                'success': True,
                'mensaje': f'Emisora con ID {emisora_id} eliminada correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la emisora con el ID proporcionado o no se pudo eliminar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar emisora: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
