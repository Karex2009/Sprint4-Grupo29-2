import os
import functools
from flask import Flask, render_template, request, flash, session, g, redirect, url_for
import utils
from db import get_db, close_db
from werkzeug.security import generate_password_hash, check_password_hash

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
                flash(error)
                return render_template('login.html')

            if not password:
                error = 'Contraseña requerida'
                flash(error)
                return render_template('login.html')
            print("validando el ingreso")
            user = db.execute(
                'SELECT * FROM personas WHERE correo = ? ', (username,)
            ).fetchone()
            
            contrasena_almacenada = user[4]
            resultado = check_password_hash(contrasena_almacenada, password)
            

            if (user is not None) and (resultado is True):
                error = 'Consulta realizada : Usuario valido'
                session.clear()
                session["user_id"]=user[3]
                session["rol"]=user[5]                
                return redirect(url_for( 'consultas' ))
            else:
                error = 'Consulta realizada : Usuario o contraseña inválidos'
            print(error)
        return render_template('login.html')
    except:
        return render_template('login.html')


@app.before_request
def load_logged_in_user():
    print("Entre al before request :)")
    user_id=session.get('user_id')
    user_rol=session.get('rol')
    print(user_id)
    
    if(user_id is None):
        g.user=None
        
    else:
        g.user = get_db().execute(
            'SELECT * FROM personas WHERE correo = ?', (user_id,)
        ).fetchone()

def login_required(view): # usuario requerido , es como si estuviese llamando directamente a la funcion interna
    @functools.wraps(view)
    def wrapped_view(**kwargs): # toma una funcion utilizada en un decorador y añadir la funcion de copia el nombre de la funcion
        if g.user is None:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view


@app.route('/registro', methods=('GET', 'POST'))
def signup():
    try:
        if request.method == 'POST':

            nombre = request.form['nombre']
            apellido = request.form['apellido']
            identificacion = request.form['identificacion']
            correo = request.form['correo']
            password = request.form['password1']
            error = None
            db = get_db()

            if error is not None:
                return render_template("registro.html")
            else:
                print("Entre a esta metodo")

                db.execute(
                     'INSERT INTO personas (nombre, apellido, identificacion, correo, contrasena,tipo_usuario) VALUES (?,?,?,?,?,?)',
                     (nombre, apellido, identificacion, correo,
                      generate_password_hash(password), 1)
                )
                db.commit()

                print('ingresado a la base de datos')
                return redirect(url_for( 'login' ))
        return render_template('registro.html')
    except:
       return render_template('registro.html')


@app.route( '/logout' )
@login_required
def logout():
    session.clear()
    return redirect(url_for( 'login' ))

@app.route('/consultas', methods=('GET', 'POST'))
# @login_required
def consultas():
    try:
        if request.method == 'POST':
            print("entre por post")
            db = get_db()
            # BUSCAR LA INFORMACION EN BASE DE DATOS CON ESA CARAR
            busqueda = request.form['busqueda']
            
            cantidad = db.execute(
                'SELECT COUNT(*) FROM vuelos where codigo =' + "'"+busqueda + "'" 
            ).fetchone()
            print(cantidad)

            result = db.execute(
                'SELECT * FROM vuelos where codigo ='+ "'"+busqueda + "'"
            ).fetchall()
            print(result)

            return render_template('consultas.html', datos=result, cantidad=cantidad)
        else:
            print("entre por get")
            db = get_db()
            todos = []

            cantidad = db.execute(
                'SELECT COUNT(*) FROM vuelos'
            ).fetchone()

            codigo = db.execute(
                'select codigo from vuelos'
            ).fetchall()
            todos.append(codigo)

            avion = db.execute(
                'SELECT avion FROM vuelos'
            ).fetchall()
            todos.append(avion)

            pilotos = db.execute(
                'SELECT piloto FROM vuelos'
            ).fetchall()
            todos.append(pilotos)

            destino = db.execute(
                'SELECT destino FROM vuelos'
            ).fetchall()
            todos.append(destino)
            print(todos)

            return render_template('consultas.html', datos=todos, cantidad=cantidad)
    except:
       return render_template('consultas.html')


@app.route('/dashboard')
@login_required
def dashboard():
    if g.user[5]==3:
        db = get_db()
        todos = []

        codigo = db.execute(
            'select * from vuelos'
        ).fetchall()
        todos.append(codigo)

        usuario = db.execute(
            'SELECT COUNT(tipo_usuario) FROM personas'
        ).fetchone()
        todos.append(usuario)

        toPilotos = db.execute(
            'SELECT COUNT(tipo_usuario) FROM personas where tipo_usuario=2'
        ).fetchone()
        todos.append(toPilotos)

        toPasajeros = db.execute(
            'SELECT COUNT(tipo_usuario) FROM personas where tipo_usuario=1'
        ).fetchone()
        todos.append(toPasajeros)

        return render_template('dashboard.html', datos=todos)
    else:
        return render_template('consultas.html')


@app.route('/reservar', methods=('GET','POST'))
@login_required
def reservar():
    if g.user[5]==1:
        try:
            if request.method=='POST':

                identificacion= request.form['identificacion']
                nombre=request.form['nombre']
                apellido=request.form['apellido']        
                correo=request.form['correo']
                         
                error=None
                db=get_db()

                if error is not None:
                    return render_template("reservar.html")
                else:
                    print ('ENTRE AL METODO RESERVAR')
                    db.execute(
                        'INSERT INTO personas (nombre, apellido,identificacion,correo, tipo_usuario) VALUES (?,?,?,?,?)',
                        (nombre, apellido, identificacion,  correo, 1)
                    )
                    db.commit()

                    print('ingresado a la base de datos')
                    return render_template('login.html')
            return render_template('reservar.html')
        except:
            return render_template('reservar.html')
    else:
        return render_template('consultas.html')
    


@app.route('/crearvuelo', methods=('GET', 'POST'))
@login_required
def crearvuelo():
    if g.user[5]==3:
        datos = []
        try:
            db = get_db()
            pilotos = db.execute(
                'SELECT nombre FROM personas WHERE tipo_usuario = 2'
            ).fetchall()
            datos.append(pilotos)
            ciudades = db.execute(
                'select * from ciudades'
            ).fetchall()
            datos.append(ciudades)
            aviones = db.execute(
                'select matricula from aviones'
            ).fetchall()
            datos.append(aviones)

            if request.method == 'POST':
                print("entre por aqui")
                codigo = request.form['codigo']
                piloto = request.form['piloto']
                destino = request.form['destino']
                avion = request.form['avion']
                puerta = request.form['puerta']
                fecha = request.form['fecha']
                hora = request.form['hora']

                db = get_db()
                db.execute(
                    'INSERT INTO vuelos (codigo, piloto, destino, avion, puerta, fecha, hora) VALUES (?,?,?,?,?,?,?)',
                    (codigo, piloto, destino, avion, puerta, fecha, hora)
                )
                db.commit()
                return render_template('crearvuelo.html', listas=datos)
            else:
                return render_template('crearvuelo.html', listas=datos)
        except:
            return render_template('crearvuelo.html')
    else:
        return render_template('consultas.html')
    


@app.route('/eliminarvuelo', methods=('GET','POST'))
@login_required
def eliminarvuelo():
    global resultadoE
    if g.user[5]==3:
        try:
            if request.method=='POST':
                db=get_db()
                buscar=request.form['buscar']
                error=None

                if not buscar :
                    error='Debes ingresar un codigo de vuelo'
                    print ( error )
                    return render_template("eliminarvuelo.html")

                # else:
                #print("Entre a metodo eliminar")
                resultadoE=db.execute(
                    'SELECT* FROM vuelos WHERE codigo=?',(buscar,)
                ).fetchone()
                print (resultadoE)

                if resultadoE is None :
                    error='ESE CODIGO DE VUELO NO EXISTE'
                    print (error)
                    return render_template("eliminarvuelo.html")
                else:
                    print ('SI SE ENCONTRO EL CODIGO DE VUELO')
                    return render_template("eliminarvuelo.html",resultados=resultadoE)         
                    
            return render_template("eliminarvuelo.html")
        except:
            return render_template('eliminarvuelo.html')
    else:
        return render_template('consultas.html')
    
@app.route('/eliminarvuelo/eliminar', methods=('GET', 'POST'))
@login_required
def eliminarvuelos():
    if g.user[5]==3:
        try:
            if request.method=='POST':
                db=get_db()
                error=None               
                db.execute(
                    'DELETE FROM vuelos WHERE codigo=?', (resultadoE[0],)
                )
                db.commit()

                print('eliminado de la base de datos')
                return render_template("eliminarvuelo.html")
            return render_template('eliminarvuelo.html')    
        except:
            return render_template('eliminarvuelo.html')
    else:
        return render_template('consultas.html')              

@app.route('/editarvuelo', methods=('GET','POST'))
@login_required
def editarvuelo():
    global resultadoA
    if g.user[5]==3:
        try:
            if request.method=='POST':
                db=get_db()
                buscar=request.form['buscar']
                error=None

                if not buscar :
                    error='Debes ingresar un codigo de vuelo'
                    print ( error )
                    return render_template("editarvuelo.html")

                else:
                    print("Entre a metodo editar")
                resultadoA=db.execute(
                    'SELECT* FROM vuelos WHERE codigo=?',(buscar,)
                ).fetchone()
                print (resultadoA)

                if resultadoA is None :
                    error='ESE CODIGO DE VUELO NO EXISTE'
                    print (error)
                    return render_template("editarvuelo.html")
                else:
                    print ('SI SE ENCONTRO EL CODIGO DE VUELO')
                    return render_template("editarvuelo.html",resultados=resultadoA)         
                    
            return render_template("editarvuelo.html")
        except:
            return render_template('editarvuelo.html')        
    else:
        return render_template('consultas.html')

@app.route('/editarvuelo/editar', methods=('GET', 'POST'))
@login_required
def editarvuelos():
    if g.user[5]==3:    
        try:
            if request.method=='POST':
                # buscar=request.form['buscar']
                fecha=request.form['fecha']
                hora=request.form['hora']
                destino=request.form['destino']
                avion=request.form['avion']
                piloto=request.form['piloto']
                puerta=request.form['puerta']   

                print('se ingreso al metodo de actualizacion')
                print(resultadoA[0])

                db=get_db()
                error=None               
                db.execute(
                    'UPDATE vuelos SET fecha=?, hora=?, destino=?,avion=?, piloto=?, puerta=? WHERE codigo= ?', (fecha,hora,destino,avion, piloto,puerta,resultadoA[0])
                )
                db.commit()

                print('Editado en la base de datos')
                return render_template("editarvuelo.html")
            return render_template('editarvuelo.html')    
        except:
            return render_template('editarvuelo.html') 
    else:
        return render_template('consultas.html')   


@app.route('/evaluar', methods=('GET','POST'))
@login_required
def evaluar():
    if g.user[5]==1:
        try:
            
            if request.method == 'POST':
                
                seguridad = request.form['seguridad']
                amabilidad2 = request.form['amabilidad2']
                comodidad2=request.form['comodidad2']
                banos=request.form['banos']
                puntualidadAbordar=request.form['puntualidadAbordar']
                puntualidadDespegue=request.form['puntualidadDespegue']
                atencion=request.form['atencion']
                amabilidad1=request.form['amabilidad1']
                refrigerio=request.form['refrigerio']
                duracion=request.form['duracion']
                comentario=request.form['comentario']
                error = None
                print('se ingreso al metodo de evaluacion')
                db = get_db()
                if error is not None:
                    return render_template("evaluar.html")
                else:
                    print ('ENTRE AL METODO INSERTAR')
                    db.execute(
                        'INSERT INTO evaluacion (seguridad, amabilidad2,comodidad2,banos, puntualidadAbordar, puntualidadDespegue,atencion,amabilidad1,refrigerio,duracion,comentario) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                        (seguridad, amabilidad2,comodidad2,banos, puntualidadAbordar, puntualidadDespegue,atencion,amabilidad1,refrigerio,duracion, comentario)
                    )
                    db.commit()
                    return render_template('consultas.html')
            return render_template('evaluar.html')
            
        except:
            return render_template('evaluar.html')
    else:
        return render_template('consultas.html')
    


@app.route('/permisos', methods=('GET', 'POST'))
@login_required
def asignarPermisos():
    global userG
    if g.user[5]==3:
        try:
            if request.method == 'POST':
                            
                db = get_db()
                error = None
                username = request.form['user']  

                if not username:
                    error = 'Debes ingresar el usuario'
                    flash( error )
                    return render_template( 'permisos.html' )
    
                userG = db.execute(
                    'SELECT * FROM personas WHERE correo = ? ', (username,)
                ).fetchone()
                print(userG)
                
                return render_template('permisos.html', usuarios=userG)

            return render_template('permisos.html')

        except:
            return render_template('permisos.html')
    else:
            return render_template('consultas.html')
        


@app.route('/permisos/act_rol', methods=('GET', 'POST'))
@login_required
def update_rol():
    if g.user[5]==3:
        try:
            if request.method == 'POST':

                seleccion = request.form['seleccion']
                db = get_db()
                error = None
                
                seleccion = int(request.form['seleccion']) 

                if error is not None:
                    return render_template("permisos.html")
                else:
                    db.execute(
                        'UPDATE personas SET tipo_usuario = ? WHERE correo = ? ', (seleccion, userG[3],)
                    )
                    db.commit()
                    error = "Rol actualizado con éxito"
                    flash(error)
                    return redirect(url_for( 'permisos' ))
                            
            return render_template('permisos.html')
        except:
            return render_template('permisos.html')

    else:
            return render_template('consultas.html')
