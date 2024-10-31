from flask import Blueprint, render_template
from app.dao.referenciales.cliente.ClienteDao import ClienteDao

climod = Blueprint('cliente', __name__, template_folder='templates')

@climod.route('/cliente-index')
def clienteIndex():
    clidao = ClienteDao()
    return render_template('cliente-index.html', clientes = clidao.getClientes())