from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.persona.PersonaDao import PersonaDao

perapi = Blueprint('perapi', __name__)

@perapi.route('/personas', methods=['GET'])
def getPersonas():
    personadao = PersonaDao()

    try:
        personas = personadao.getPersonas()

        return jsonify({
            'success': True,
            'data': personas,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todas las personas: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@perapi.route('/personas/<int:id_persona>', methods=['GET'])
def getPersona(id_persona):
    personadao = PersonaDao()

    try:
        persona = personadao.getPersonaById(id_persona)

        if persona:
            return jsonify({
                'success': True,
                'data': persona,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la persona con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener persona: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@perapi.route('/personas', methods=['POST'])
def addPersona():
    data = request.get_json()
    personadao = PersonaDao()

    campos_requeridos = ['nombres', 'apellidos', 'nro_cedula', 'fecha_nacimiento', 'direccion']

    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or len(data[campo].strip()) == 0:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    try:
        id_persona = personadao.guardarPersona(
            data['nombres'].strip().upper(),
            data['apellidos'].strip().upper(),
            data['nro_cedula'],
            data['fecha_nacimiento'],
            data['direccion'].strip().upper() 
        )
        
        return jsonify({
            'success': True,
            'data': {
                'id_persona': id_persona,
                'nombres': data['nombres'].upper(),
                'apellidos': data['apellidos'].upper(),
                'nro_cedula': data['nro_cedula'],
                'fecha_nacimiento': data['fecha_nacimiento'],
                'direccion': data['direccion'].upper() 
            },
            'error': None
        }), 201

    except Exception as e:
        app.logger.error(f"Error al agregar persona: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@perapi.route('/personas/<int:id_persona>', methods=['PUT'])
def updatePersona(id_persona):
    data = request.get_json()
    personadao = PersonaDao()

    campos_requeridos = ['nombres', 'apellidos', 'nro_cedula', 'fecha_nacimiento', 'direccion']

    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or len(data[campo].strip()) == 0:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    try:
        if personadao.updatePersona(
            id_persona,
            data['nombres'].strip().upper(),
            data['apellidos'].strip().upper(),
            data['nro_cedula'],
            data['fecha_nacimiento'],
            data['direccion'].strip().upper() 
        ):
            return jsonify({
                'success': True,
                'data': {
                    'id_persona': id_persona,
                    'nombres': data['nombres'].upper(),
                    'apellidos': data['apellidos'].upper(),
                    'nro_cedula': data['nro_cedula'],
                    'fecha_nacimiento': data['fecha_nacimiento'],
                    'direccion': data['direccion'].upper()  
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la persona con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar persona: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@perapi.route('/personas/<int:id_persona>', methods=['DELETE'])
def deletePersona(id_persona):
    personadao = PersonaDao()

    try:
        if personadao.deletePersona(id_persona):
            return jsonify({
                'success': True,
                'mensaje': f'Persona con ID {id_persona} eliminada correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la persona con el ID proporcionado o no se pudo eliminar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar persona: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
