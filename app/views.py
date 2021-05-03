from app import app
from flask import Flask, render_template, url_for, request, redirect, flash, session, make_response
from flaskext.mysql import MySQL
#from flask_mysqldb import MySQL
import bcrypt
import time
from dotenv import load_dotenv
load_dotenv
import os
salt = bcrypt.gensalt()
#------------------Inicializo BBDD------------------------
#Config de la BBDD
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Mysql1234'
app.config['MYSQL_DATABASE_DB'] = 'flask_usuarios'
mysql = MySQL(app)

#Cómo va protegida la sesión
app.secret_key='mysecretkey'

@app.route('/env')
def env():
    return f'Hello, {os.getenv("SECRET_VALUE")} the meaning of life is {os.getenv("MEANING_OF_LIFE")}'

@app.route('/')
def main():
    if 'nombre' in session:
        perfil = session.get('perfil')
        if (perfil == 'Administrador'):
            return render_template("admin/index.html")
        elif(perfil != 'Administrador'):
            return render_template("noadmin/index.html")
    else:
        return render_template("login.html")

@app.route('/index')
def index():
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/index.html")
    else:
        return render_template("noadmin/index.html")

#------------------------------ADMINISTRACIÓN--------------------------------------------------------

@app.route('/registro', methods = ["GET", "POST"])
def registro():
    if request.method == "GET":
        return render_template("admin/registroframe.html")
    else:
            import time
            ts=time.time()
            print(time.ctime(ts))
            nombre = request.form["nombreRegistro"]
            email = request.form["emailRegistro"]
            perfil = request.form["perfilRegistro"]
            password = request.form["passwordRegistro"]
            password_encode = password.encode("utf-8")
            password_encriptada = bcrypt.hashpw(password_encode, salt)
            if nombre == "":
                flash("Debe indicar su nombre")
                return redirect (url_for("registro"))
            if email == "":
                flash("Debe indicar su correo electrónico")
                return redirect (url_for("registro"))
            if perfil == "Noseleccionado":
                flash("Debe indicar su tipo de perfil")
                return redirect (url_for("registro"))
            if password == "":
                flash("Debe indicar su contraseña")
                return redirect (url_for("registro"))
            
            cur = mysql.get_db().cursor()
            consulta='SELECT  iduser, nombre, email, perfil, password FROM usuarios where email =%s'
            cur.execute(consulta, [email])
            row = cur.fetchone()
            if row == None:
                 cur.execute('INSERT INTO usuarios (nombre, email, perfil, password) VALUES (%s,%s,%s,%s)', (nombre, email, perfil,password_encriptada))
                 mysql.get_db().commit()
            else:
                flash("Ya existe un usuario con dicho correo electrónico")
                return redirect(url_for("registro"))
        
        
    return redirect(url_for('index')) #PORQUE SE REGISTRA DESDE DENTRO
@app.route('/login', methods = ["GET", "POST"])
def login():
    if request.method == "GET":
          return render_template("login.html")
    else:
        import time
        ts=time.time()
        tord=time.ctime(ts)
        print(tord)
        email = request.form["emailLogin"] 
        password = request.form["passwordLogin"]
        password_encode = password.encode("utf-8")

        if email == "":
            flash("Debe indicar su correo electrónico")
            return redirect (url_for("login"))
        if password == "":
            flash("Debe indicar su contraseña")
            return redirect (url_for("login"))

        cur = mysql.get_db().cursor()
        consulta='SELECT iduser, nombre, email, perfil, password FROM usuarios where email =%s'
        cur.execute(consulta, [email])
        row = cur.fetchone()
        
        

        if (row != None):
            password_encriptada_encode = row[4].encode()
            if (bcrypt.checkpw(password_encode, password_encriptada_encode)):
                session["id"]= row[0]
                session["nombre"] = row[1]
                session["email"] = row[2]
                session["perfil"] = row[3]

                consulta2= 'SELECT idactions FROM actions WHERE title LIKE "%login%"' 
                cur.execute(consulta2)
                act=cur.fetchone()

                consulta3= 'SELECT iduser FROM usuarios WHERE email=%s'
                cur.execute(consulta3, [email])
                id = cur.fetchone()
                
                cur.execute('INSERT INTO user_action (id_user, action) VALUES (%s,%s)', (id,act))
                mysql.get_db().commit()
                cur.close()
                return redirect(url_for("main"))
            else:
                flash("Las credenciales introducidas son incorrectas")
                return(render_template("login.html"))
        if( row == None):
            flash("Las credenciales introducidas son incorrectas")
            return (render_template("login.html"))

@app.route('/usuarios_registrados')
def usuarios_registrados():
    cur = mysql.get_db().cursor()
    cur.execute('SELECT * FROM usuarios')
    data = cur.fetchall()
    return render_template("admin/usuariosregistrados.html", contacts = data)

@app.route('/delete/<string:email>')
def delete_contact(email):
    cur = mysql.get_db().cursor()
    consulta = ('DELETE FROM usuarios WHERE email = %s LIMIT 1')
    cur.execute(consulta, [email])
    mysql.get_db().commit()
    flash('Usuario eliminado correctamente')
    return redirect(url_for("usuarios_registrados"))

@app.route('/edit/<string:email>')
def get_contact(email):
    cursor = mysql.get_db().cursor()
    consulta= ('SELECT * FROM usuarios WHERE email= %s')
    cursor.execute(consulta, [email])
    data= cursor.fetchall()
    return render_template('admin/usuarioseditados.html', contact = data[0])

@app.route('/update/<string:email>',methods= ['POST'])
def update_contact(email):
    if request.method == 'POST':
        nombre = request.form['nombreActualizado']
        email = request.form['emailActualizado'] 
        perfil= request.form['perfilActualizado']
    
        cursor = mysql.get_db().cursor()
        cursor.execute( """
            UPDATE usuarios
            SET nombre= '{0}',
                email = '{1}',
                perfil = '{2}'
            WHERE email = '{1}'"""
            .format(nombre,email,perfil))
        mysql.get_db().commit() 
        flash("Contacto actualizado satisfactoriamente")
        return redirect(url_for('usuarios_registrados'))

@app.route('/perfiles')
def perfiles():
    return render_template("admin/perfiles.html")

@app.route('/acciones')
def acciones():
    cur = mysql.get_db().cursor()
    cur.execute('SELECT * FROM user_action')
    data = cur.fetchall()
    cur.execute('SELECT nombre,email FROM usuarios INNER JOIN user_action ON usuarios.iduser=user_action.id_user GROUP BY timestamp')
    dato = cur.fetchall()
    return render_template("admin/acciones.html", acciones= data, usuarios = dato)

#-------------------------------------------GESTIÓN-----------------------------------------------------------------
#-----------------------SENSORES------------------------------------------------------------------------------------
@app.route('/sensoresWF')
def sensoresWF():
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/sensoresWF.html")
    elif(perfil != 'Administrador'):
        return render_template("noadmin/sensoresWF.html")
@app.route('/sensoresBT')
def sensoresBT():
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/sensoresBT.html")
    elif(perfil != 'Administrador'):
        return render_template("noadmin/sensoresBT.html")
@app.route('/sensoresRF')
def sensoresRF():
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/sensoresRF.html")
    elif(perfil != 'Administrador'):
        return render_template("noadmin/sensoresRF.html")
@app.route('/sensoresRM')
def sensoresRM():
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/sensoresRM.html")
    elif(perfil != 'Administrador'):
        return render_template("noadmin/sensoresRM.html")
#-----------------------SUBSISTEMAS------------------------------------------------------------------------------------
@app.route('/subsistemaBD')
def subsistemaBD():
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/subsistemaBD.html")
    elif(perfil != 'Administrador'):
        return render_template("noadmin/subsistemaBD.html")
@app.route('/grupos')
def grupos():
    grupo = {os.getenv("GRUPO_WIFI")}
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/grupo.html", grupo=grupo)
    elif(perfil != 'Administrador'):
        return render_template("noadmin/sensores.html")

@app.route('/salir')
def salir():
    session.clear()
    return redirect(url_for("main"))

@app.route('/helloworld')
def hello_world():
    resp = make_response(render_template("admin/sensores.html"))
    # Set a same-site cookie for first-party contexts
    resp.set_cookie('cookie1', 'value1', samesite='None')
    # Ensure you use "add" to not overwrite existing cookie headers
    # Set a cross-site cookie for third-party contexts
    resp.headers.add('Set-Cookie','cookie2=value2; SameSite=None; Secure') #nombre=valor
    return resp
@app.route('/cookie')
def cookie():
    resp = make_response(render_template('admin/sensores.html'))
    resp.set_cookie('somecookiename', 'I am cookie')
    resp.set_cookie(
        "somecookiename",
        value= "I am a cookie",
        max_age=25630,
        expires=None,
        path = request.path,
        domain= ".app.localhost", #dominio que puede leer la cookie
        secure= False,
        httponly=False, #el pone false
        samesite= None
        )
    return resp
@app.route('/get-cookie/')
def get_cookie():
    username = request.cookies.get('somecookiename')
    return username
@app.route('/time')
def time():
    import time
    from datetime import datetime

    start_time = time.process_time()

    ts=time.time()
    print(ts) #segundos desde epoch con precisión de microsegundos (epoch=1 enero 1970)
    print(time.ctime(ts)) #convertido a tiempo del ordenador

    now= datetime.fromtimestamp(ts)#convertido a fecha separada por guiones y hora
    print(now)

    end_time = time.process_time()

    print("tiempo de duración =", end_time-start_time)
    return "hola"

@app.route('/cookiejn')
def cookiejn():
    res = make_response("Cookies" , 200)
    cookies = request.cookies
    flavor = cookies.get("flavor")
    choctype = cookies.get("chocolate type")
    smel = cookies.get("smell")
    print(flavor, smel, choctype)
    
    res.set_cookie(
        "flavor",
        value= "chocolate chip",
        max_age=10,
        expires=None,
        path=request.path,
        domain=None, #dominio que puede leer la cookie
        secure= False,
        httponly=False, #el pone false
        samesite= None
        )
    res.set_cookie("chocolate type", "milka")
    res.set_cookie("smell", "lemon")
    
    return res