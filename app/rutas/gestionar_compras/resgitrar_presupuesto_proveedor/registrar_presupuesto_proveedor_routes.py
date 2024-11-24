from flask import Blueprint, render_template

pdpmod = Blueprint('pdpmod', __name__, template_folder='templates')

@pdpmod.route('/presupuestos-index')
def presupuestos_index():
    return render_template('presupuestos-index.html')

@pdpmod.route('/presupuestos-agregar')
def presupuestos_agregar():
    return render_template('presupuestos-agregar.html')