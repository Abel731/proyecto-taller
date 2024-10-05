from flask import Blueprint, render_template

tipprodmod = Blueprint('tipo_producto', __name__, template_folder='templates')

@tipprodmod.route('/tipo_producto-index')
def tipo_productoIndex():
    return render_template('tipo_producto-index.html')