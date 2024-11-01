from flask import Blueprint, render_template
from app.dao.referenciales.persona.PersonaDao import PersonaDao

climod = Blueprint('cliente', __name__, template_folder='templates')

@climod.route('/cliente-index')
def clienteIndex():
    perdao = PersonaDao()
    return render_template('cliente-index.html', clientes = perdao.getPersonas())