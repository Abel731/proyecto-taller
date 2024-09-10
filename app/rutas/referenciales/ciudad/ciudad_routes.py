from flask import Blueprint, render_template, request, flash, url_for, redirect
from app.dao.referenciales.ciudad.CiudadDao import CiudadDao

ciumod = Blueprint('ciudad', __name__, template_folder='templates')

ciumod.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@ciumod.route('/ciudad-index')
def ciudadIndex():
    ciudadDao = CiudadDao()
    return render_template('ciudad-index.html', lista_ciudades=ciudadDao.getCiudades())

@ciumod.route('/ciudad-agregar')
def ciudadAgregar():
    return render_template('ciudad-agregar.html')

@ciumod.route('/guardar-ciudad', methods=['POST'])
def guardarCiudad():
    ciudad = request.form.get('txtDescripcion').strip()
    if ciudad == None or len(ciudad) < 1:
        # mostrar un mensaje al usuario
        flash('Debe escribir algo en la descripcion', 'warning')

        # redireccionar a la vista ciudades
        return redirect(url_for('ciudadAgregar'))

    ciudaddao = CiudadDao()
    ciudaddao.guardarCiudad(ciudad.upper())

    # mostrar un mensaje al usuario
    flash('Guardado exitoso', 'success')

    # redireccionar a la vista ciudades
    return redirect(url_for('ciudadIndex'))