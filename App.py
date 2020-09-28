from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import hashlib


app = Flask(__name__)

#conexion a MysQl
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'contactos'
mysql = MySQL(app)

#configuraciones
app.secret_key='Mi llave secreta'


@app.route('/')
def main():
    if 'Correo' in session:
        return redirect(url_for('Principal'))
    else:
        return render_template('ingresar.html')


@app.route('/ingresar')
def Ingresar():
    if 'Correo' in session:
        return render_template('principal.html')
    else:
        return render_template('ingresar.html')

@app.route('/registrar')
def Registrar():
    return render_template('registrar.html')


@app.route('/principal')
def Principal():
    if 'Correo' in session:

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM contactos')
        dato = cur.fetchall()
        return render_template('principal.html', contacto = dato)
    else:
        return render_template('ingresar.html')


@app.route('/add_contact', methods=['POST'])
def add_contact():
    
    if request.method =='POST':
        nombre = request.form['Nombre']
        telefono = request.form['Telefono']
        correo = request.form['Correo']
        contraseña = request.form['Contraseña']
        ePass=hashlib.sha512(contraseña.encode())
        n=ePass.hexdigest()
        contraseña2 = request.form['Contraseña2']
        ePass2 = hashlib.sha512(contraseña2.encode())
        n2 = ePass2.hexdigest()

        if len (nombre) == 0:
            flash('se requiere un nombre')
            return redirect(url_for('Registrar'))

        elif len(telefono) == 0:
            flash('se requiere un telefono')
            return redirect(url_for('Registrar'))

        elif len(correo) == 0:
            flash('se requiere un correo')
            return redirect(url_for('Registrar'))

        elif len(contraseña) == 0:
            flash('se requiere una contraseña')
            return redirect(url_for('Registrar'))

        else:
            if (n == n2):

                cur = mysql.connection.cursor()
                cur.execute('SELECT Correo FROM contactos WHERE Correo = %s', [correo])
                mysql.connection.commit()
                usuario = cur.fetchone()

                if(usuario != None ):
                    flash('correo registrado, por favor ingrese un correo diferente')
                    return redirect(url_for('Registrar'))
                else:
                    cur.execute('INSERT INTO contactos (Nombre, Telefono, Correo, Contraseña) VALUES(%s, %s, %s, %s)',
                                (nombre, telefono, correo, n))
                    mysql.connection.commit()
                    flash('Contacto agregado')
                    return redirect(url_for('Principal'))

            else:
                flash('ingreso una contraseña diferente')
                return redirect(url_for('Registrar'))


@app.route('/edit/<id>')
def get_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contactos WHERE id = %s', [id])
    dato = cur.fetchall()
    return render_template('editarContacto.html', contacto=dato[0])

@app.route('/update/<id>', methods = ['POST'])
def update_contact(id):
    if request.method == 'POST':
        nombre = request.form['Nombre']
        telefono = request.form['Telefono']
        correo = request.form['Correo']
        cur = mysql.connection.cursor()
        cur.execute('UPDATE contactos SET Nombre = %s, Telefono = %s, Correo = %s WHERE id = %s',
                    (nombre, telefono, correo, id))
        mysql.connection.commit()
        flash('Contacto actualizado')
        return redirect(url_for('Principal'))



@app.route('/delete/<string:id>')
def delete(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM contactos WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Contacto Eliminado')
    return redirect(url_for('Principal'))

@app.route('/login', methods = ['POST'])
def login():
    if request.method == 'POST':
        correo = request.form['Correo']
        contraseña = request.form['Contraseña']
        ePass = hashlib.sha512(contraseña.encode())
        n = ePass.hexdigest()
        cur = mysql.connection.cursor()
        cur.execute('SELECT Correo, Contraseña FROM contactos WHERE Correo = %s', [correo])
        mysql.connection.commit()
        usuario = cur.fetchone()

        if (usuario != None):

            if (usuario[1]==n):

                session['Correo'] = correo

                if 'Correo' in session:

                    return redirect(url_for('Principal'))
            else:
                flash('Contraseña incorrecta')
                return redirect(url_for('Ingresar'))
        else:

            flash('Usuario no existe')
            return redirect(url_for('Ingresar'))

@app.route('/salir')
def salir():
    session.clear()
    return redirect(url_for('Ingresar'))

if __name__ == '__main__':
    app.run(port=3000, debug=True)
