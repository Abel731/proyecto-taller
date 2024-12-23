from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.dao.login.login_dao import validar_usuario

# Crear el Blueprint
login_bp = Blueprint('login', __name__, template_folder='templates')

# Ruta para mostrar el formulario de login
@login_bp.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

# Ruta para procesar el login
@login_bp.route('/login', methods=['POST'])
def login_post():
    usuario_input = request.form['usuario']
    clave_input = request.form['clave']

    # Validar el usuario y la contraseña
    usuario = validar_usuario(usuario_input, clave_input)

    if usuario:
        # Si el usuario es válido, almacenamos los datos en la sesión
        session['id_usuario'] = usuario['id_usuario']
        session['usuario'] = usuario['usuario']
        session['roles'] = usuario['roles']
        
        # Redirigimos a la página principal o dashboard
        return render_template('inicio.html')
    else:
        # Si las credenciales son incorrectas, mostramos un mensaje de error
        flash('Usuario o contraseña incorrectos', 'error')
        return redirect(url_for('login.login'))
@login_bp.route('/logout')
def logout():
    session.clear()  # Limpiar cualquier sesión previa
    flash('Sesión cerrada', 'warning')  # Mostrar mensaje de sesión cerrada
    return redirect(url_for('login.login'))  

@login_bp.route('/')
def inicio():
    if 'usuario' in session:
        return redirect(url_for('login.login'))
    else:
        return redirect(url_for('login.login'))    