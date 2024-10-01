from flask import Blueprint, render_template

carmod = Blueprint('cargo', __name__, template_folder='templates')

@carmod.route('/cargo-index')
def cargoIndex():
    return render_template('cargo-index.html')