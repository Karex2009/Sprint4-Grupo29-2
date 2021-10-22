import os
from flask import Flask, render_template,request,flash
import utils
from db import get_db,close_db

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    try:
        if request.method == 'POST':
            db = get_db()
            error = None
            username = request.form['correo']
            password = request.form['password']
            if not username:
                error = 'Debes ingresar el usuario'
                flash( error )
                return render_template( 'login.html' )

            if not password:
                error = 'Contraseña requerida'
                flash( error )
                return render_template( 'login.html' )
            print("validando el ingreso")    
            user = db.execute(
                'SELECT * FROM personas WHERE correo = ? AND contrasena = ? ', (username, password)
            ).fetchone()

            if user is None:
                error = 'Consulta realizada : Usuario o contraseña inválidos'
            else:
                error = 'Consulta realizada : Usuario valido'
            print(error)
            return render_template('dashboard.html')
        return render_template( 'login.html' )
    except:
        return render_template( 'login.html' )
    

@app.route('/registro', methods=('GET', 'POST'))
def signup():
    try:
        if request.method=='POST':

            nombre=request.form['nombre']
            apellido=request.form['apellido']
            identificacion= request.form['identificacion']
            correo=request.form['correo']
            password=request.form['password1']
            error=None
            db=get_db()

            if error is not None:
                return render_template("registro.html")
            else:
                print("Entre a esta metodo")

                db.execute(
                     'INSERT INTO personas (nombre, apellido, identificacion, correo, contrasena,tipo_usuario) VALUES (?,?,?,?,?,?)',
                     (nombre, apellido, identificacion, correo, password,1)
                )
                db.commit()
               
                print('ingresado a la base de datos')
                return render_template('login.html')
        return render_template('registro.html')
    except:
       return render_template('registro.html')


@app.route('/consultas')
def consultas():
    return render_template('consultas.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/reservar')
def reservar():
    return render_template('reservar.html')

@app.route('/crearvuelo')
def crearvuelo():
    return render_template('crearvuelo.html')

@app.route('/eliminarvuelo')
def eliminarvuelo():
    return render_template('eliminarvuelo.html')

@app.route('/editarvuelo')
def editarvuelo():
    return render_template('editarvuelo.html')

@app.route('/evaluar')
def evaluar():
    return render_template('evaluar.html')