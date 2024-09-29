from flask import Blueprint, render_template

promod = Blueprint('producto', __name__, template_folder='templates')

@promod.route('/producto-index')
def productoIndex():
    return render_template('producto-index.html')