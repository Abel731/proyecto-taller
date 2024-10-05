from flask import Blueprint, render_template

emismod = Blueprint('emisora', __name__, template_folder='templates')

@emismod.route('/emisora-index')
def emisoraIndex():
    return render_template('emisora-index.html')