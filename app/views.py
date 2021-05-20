from app import app
from flask import Flask, render_template, url_for, request, redirect, flash, session, make_response
from flaskext.mysql import MySQL
#from flask_mysqldb import MySQL
import bcrypt
import time
from dotenv import load_dotenv
load_dotenv
import os
import Crypto
import binascii
from Crypto.PublicKey import RSA 
from Crypto.Cipher import PKCS1_OAEP #genera objeto cipher que permite cifrar
import subprocess
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
                 
                consulta2= 'SELECT idactions FROM actions WHERE title LIKE "%registro%"' 
                cur.execute(consulta2)
                act=cur.fetchone()

                consulta3= 'SELECT iduser FROM usuarios WHERE email=%s'
                cur.execute(consulta3, [email])
                id = cur.fetchone()
                
                cur.execute('INSERT INTO user_actions (id_user, action) VALUES (%s,%s)', (id,act))
                mysql.get_db().commit()
                cur.close()
                
            else:
                flash("Ya existe un usuario con dicho correo electrónico")
                return redirect(url_for("registro"))
        
        
    return redirect(url_for('index')) #PORQUE SE REGISTRA DESDE DENTRO
@app.route('/login', methods = ["GET", "POST"])
def login():
    if request.method == "GET":
          return render_template("login.html")
    else:
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
                
                cur.execute('INSERT INTO user_actions (id_user, action) VALUES (%s,%s)', (id,act))
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

@app.route('/delete/<int:iduser>')
def delete_contact(iduser):
    cur = mysql.get_db().cursor()
    consulta1 = ('DELETE FROM user_actions WHERE id_user= %s LIMIT 1')
    consulta2 = ('DELETE FROM usuarios WHERE iduser = %s LIMIT 1')
    cur.execute(consulta1, [iduser])
    cur.execute(consulta2, [iduser])
    mysql.get_db().commit()
    cur.close()
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
    cur.execute('SELECT fm.nombre, fm.email, f.timestamp, f.action FROM user_actions AS f JOIN usuarios AS fm ON fm.iduser=f.id_user GROUP BY f.timestamp ORDER BY f.timestamp DESC')
    datos = cur.fetchall()
    #cur.execute('SELECT action,timestamp FROM user_actions')
    #data = cur.fetchall()
    #cur.execute('SELECT nombre,email FROM usuarios INNER JOIN user_actions ON usuarios.iduser=user_actions.id_user GROUP BY timestamp')
    #dato = cur.fetchall()
    return render_template("admin/acciones.html", datos= datos)
    #acciones= data, usuarios = dato)

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

@app.route('/delete/sensor/<int:idsensores>')
def delete_sensor(idsensores):
    cur = mysql.get_db().cursor()
    consulta = ('DELETE FROM sensores WHERE idsensores= %s LIMIT 1')
    cur.execute(consulta, [idsensores])
    mysql.get_db().commit()
    flash('Sensor eliminado correctamente')
    return redirect(url_for("sensores"))

@app.route('/edit/sensor/<int:idsensores>')
def get_sensor(idsensores):
    cursor = mysql.get_db().cursor()
    consulta= ('SELECT * FROM sensores WHERE idsensores= %s')
    cursor.execute(consulta, [idsensores])
    sensor= cursor.fetchall()
    return render_template('admin/sensoreseditados.html', sensores = sensor[0])

@app.route('/update/sensores/<int:idsensores>',methods= ['POST'])
def update_sensor(idsensores):
    if request.method == 'POST':
        nombre = request.form['nombreActualizado']
        tipo = request.form['tipoActualizado'] 
        mac= request.form['macActualizada']
        ip= request.form['ipActualizada']
    
        cursor = mysql.get_db().cursor()
        cursor.execute( """
            UPDATE sensores
            SET nombre= '{1}',
                tipo = '{2}',
                mac = '{3}',
                ip = '{4}'
            WHERE idsensores = '{0}'"""
            .format(idsensores,nombre,tipo,mac,ip))
        mysql.get_db().commit() 
        flash("Sensor actualizado satisfactoriamente")
        return redirect(url_for('sensores'))
@app.route('/registrosensores', methods = ["GET", "POST"])
def registrosensores():
    if request.method == "GET":
        return render_template("admin/registrarsensor.html")
    else:
            nombre = request.form["nombreSensor"]
            tipo = request.form["tipoRegistro"]
            mac = request.form["macRegistro"]
            ip = request.form["ipRegistro"]
            if nombre == "":
                flash("Debe indicar un nombre")
                return redirect (url_for("registrosensores"))
            if tipo == "Noseleccionado":
                flash("Debe indicar el tipo del sensor")
                return redirect (url_for("registrosensores"))
            if mac == "":
                flash("Debe indicar una dirección MAC")
                return redirect (url_for("registrosensores")) 
                    
            
            cur = mysql.get_db().cursor()
            consulta='SELECT  idsensores, nombre, tipo, mac, ip FROM sensores WHERE mac=%s'
            cur.execute(consulta, [mac])
            row = cur.fetchone()
            if row == None:
                cur.execute('INSERT INTO sensores (nombre, tipo, mac, ip) VALUES (%s,%s,%s,%s)', (nombre, tipo, mac,ip))
                mysql.get_db().commit()
                cur.close()
                
            else:
                flash("El sensor introducido ya existe")
                return redirect(url_for("registrosensores"))
    
    return redirect(url_for('sensores')) 

@app.route('/sensores')
def sensores():
    cur = mysql.get_db().cursor()
    cur.execute('SELECT * FROM sensores')
    sensores = cur.fetchall()
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/sensores.html", sensores= sensores )
    elif(perfil != 'Administrador'):
        return render_template("noadmin/sensores.html", sensores= sensores)

@app.route('/consolaPandora')
def consolaPandora():
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/consolaPandora.html")
    elif(perfil != 'Administrador'):
        return render_template("noadmin/consolaPandora.html")

#-----------------------SUBSISTEMAS------------------------------------------------------------------------------------
@app.route('/subsistemaBD')
def subsistemaBD():
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/subsistemaBD.html")
    elif(perfil != 'Administrador'):
        return render_template("noadmin/subsistemaBD.html")
@app.route('/subsistemaAA')
def subsistemaAA():
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/subsistemaAA.html")
    elif(perfil != 'Administrador'):
        return render_template("noadmin/subsistemaAA.html")
@app.route('/subsistemaCM')
def subsistemaCM():
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/subsistemaACM.html")
    elif(perfil != 'Administrador'):
        return render_template("noadmin/subsistemaCM.html")

@app.route('/subsistemaO')
def subsistemaO():
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/subsistemaO.html")
    elif(perfil != 'Administrador'):
        return render_template("noadmin/subsistemaO.html")
@app.route('/subsistemaC')
def subsistemaC():
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/subsistemaC.html")
    elif(perfil != 'Administrador'):
        return render_template("noadmin/subsistemaC.html")

@app.route('/grupos')
def grupos():
    grupo = {os.getenv("GRUPO_WIFI")}
    print(type(grupo))
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

@app.route('/claves')
def claves():
    #Genero llaves con un random
    random_generator = Crypto.Random.new().read
    private_key = RSA.generate(1024, random_generator)
    public_key = private_key.publickey()
    #Exporto las llaves para convertirlas a utf-8
    private_key=private_key.export_key(format='PEM')
    public_key=public_key.export_key(format='PEM')

    file_out = open("private.pem", "wb")
    file_out.write(private_key)
    file_out.close()
    
    file_out = open("public.pem", "wb")
    file_out.write(public_key)
    file_out.close()
    #Convierto de binario a utf-8
    #private_key= binascii.hexlify(private_key).decode('utf-8')
    #public_key= binascii.hexlify(public_key).decode('utf-8') #la corta
    #print(private_key)
    
    #------------------------------------------------------------------------

    #CIFRO UN MENSAJE importando llaves y conviertiendo de utf-8 a binario
    #private_key=RSA.import_key(binascii.unhexlify(private_key))
    #public_key=RSA.import_key(binascii.unhexlify(public_key))

    #message="Hola mundo"
    #message=message.encode()
    #cipher= PKCS1_OAEP.new(public_key)
    #message_encrypted=cipher.encrypt(message)
    #print(message_encrypted)

    #cipher = PKCS1_OAEP.new(private_key)
    #messagef = cipher.decrypt(message_encrypted)
    #print(message)

    #print(private_key)
    #print(public_key)
    return (private_key)

@app.route('/envio')
def envio():
    subprocess.call(["scp", "root@192.168.1.159:/root", "localpath"])
    print (open("localpath").read())
