from typing import Any
from app import app
from flask import Flask, render_template, url_for, request, redirect, flash, session, make_response
from flaskext.mysql import MySQL
#from flask_mysqldb import MySQL
import bcrypt
import time
import os
import Crypto
import binascii
from Crypto.PublicKey import RSA 
from Crypto.Cipher import PKCS1_OAEP #genera objeto cipher que permite cifrar
import subprocess
from flask.helpers import send_file
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
            passwordconf = request.form["passwordRegistroconfirmacion"]
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
            if password == passwordconf:
                password_encode = password.encode("utf-8")
                password_encriptada = bcrypt.hashpw(password_encode, salt)                
            
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
            else:
                flash("Las contraseñas no coinciden")
                return redirect(url_for("registro"))
        
    return redirect(url_for('index')) 
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
    cur = mysql.get_db().cursor()
    cur.execute('SELECT * FROM usuarios WHERE perfil LIKE "%Administrador%"')
    admin = cur.fetchall()
    cur.execute('SELECT * FROM usuarios WHERE perfil LIKE "%Analista%"')
    analista = cur.fetchall()   
    cur.execute('SELECT * FROM usuarios WHERE perfil LIKE "%Operador%"')
    operador = cur.fetchall()   
    return render_template("admin/perfiles.html", p_admin=admin, p_analista=analista, p_operador=operador)

@app.route('/acciones')
def acciones():
    cur = mysql.get_db().cursor()
    cur.execute('SELECT fm.nombre, fm.email, f.timestamp, f.action FROM user_actions AS f JOIN usuarios AS fm ON fm.iduser=f.id_user GROUP BY f.timestamp ORDER BY f.timestamp DESC')
    datos = cur.fetchall()
    return render_template("admin/acciones.html", datos= datos)

#-------------------------------------------GESTIÓN-----------------------------------------------------------------
#-----------------------SENSORES------------------------------------------------------------------------------------
@app.route('/sensoresWF')
def sensoresWF():
    variable_env1 = {os.getenv("GRUPO_WIFI")}
    id_str = " ".join(variable_env1)
    #id_str="17"
    print(id_str)
    cur = mysql.get_db().cursor()
    consulta= 'SELECT idactions FROM actions WHERE title LIKE "%pandora%"' 
    cur.execute(consulta)
    act=cur.fetchone()

    consulta3= 'SELECT iduser FROM usuarios WHERE email=%s'
    cur.execute(consulta3, session.get("email"))
    id = cur.fetchone()
                    
    cur.execute('INSERT INTO user_actions (id_user, action) VALUES (%s,%s)', (id,act))
    mysql.get_db().commit()
    cur.close()
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/sensoresWF.html", idwifi=id_str)
    elif(perfil != 'Administrador'):
        return render_template("noadmin/sensoresWF.html")
@app.route('/sensoresBT')
def sensoresBT():
    variable_env2 = {os.getenv("GRUPO_BLUETOOTH")}
    idstr = " ".join(variable_env2)
    cur = mysql.get_db().cursor()
    consulta= 'SELECT idactions FROM actions WHERE title LIKE "%pandora%"' 
    cur.execute(consulta)
    act=cur.fetchone()

    consulta3= 'SELECT iduser FROM usuarios WHERE email=%s'
    cur.execute(consulta3, session.get("email"))
    id = cur.fetchone()
                    
    cur.execute('INSERT INTO user_actions (id_user, action) VALUES (%s,%s)', (id,act))
    mysql.get_db().commit()
    cur.close()
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/sensoresBT.html", id2=idstr)
    elif(perfil != 'Administrador'):
        return render_template("noadmin/sensoresBT.html")
@app.route('/sensoresRF')
def sensoresRF():
    variable_env3 = {os.getenv("GRUPO_RF")}
    idstr = " ".join(variable_env3)
    print(idstr)
    cur = mysql.get_db().cursor()
    consulta= 'SELECT idactions FROM actions WHERE title LIKE "%pandora%"' 
    cur.execute(consulta)
    act=cur.fetchone()

    consulta3= 'SELECT iduser FROM usuarios WHERE email=%s'
    cur.execute(consulta3, session.get("email"))
    id = cur.fetchone()
                    
    cur.execute('INSERT INTO user_actions (id_user, action) VALUES (%s,%s)', (id,act))
    mysql.get_db().commit()
    cur.close()
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/sensoresRF.html", id3=idstr)
    elif(perfil != 'Administrador'):
        return render_template("noadmin/sensoresRF.html")
@app.route('/sensoresRM')
def sensoresRM():
    variable_env4 = {os.getenv("GRUPO_RM")}
    idstr = " ".join(variable_env4)
    print(idstr)
    cur = mysql.get_db().cursor()
    consulta= 'SELECT idactions FROM actions WHERE title LIKE "%pandora%"' 
    cur.execute(consulta)
    act=cur.fetchone()

    consulta3= 'SELECT iduser FROM usuarios WHERE email=%s'
    cur.execute(consulta3, session.get("email"))
    id = cur.fetchone()
                    
    cur.execute('INSERT INTO user_actions (id_user, action) VALUES (%s,%s)', (id,act))
    mysql.get_db().commit()
    cur.close()
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/sensoresRM.html", id4=idstr)
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
        descripcion = request.form["descripcionActualizada"]
    
        cursor = mysql.get_db().cursor()
        cursor.execute( """
            UPDATE sensores
            SET nombre= '{1}',
                tipo = '{2}',
                mac = '{3}',
                ip = '{4}',
                descripcion = '{5}'
            WHERE idsensores = '{0}'"""
            .format(idsensores,nombre,tipo,mac,ip,descripcion))
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
            descripcion = request.form["descripcionRegistro"]

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
            consulta='SELECT  idsensores, nombre, tipo, mac, ip, descripcion FROM sensores WHERE mac=%s'
            cur.execute(consulta, [mac])
            row = cur.fetchone()
            if row == None:
                cur.execute('INSERT INTO sensores (nombre, tipo, mac, ip, descripcion) VALUES (%s,%s,%s,%s,%s)', (nombre, tipo, mac,ip,descripcion))
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
    cur = mysql.get_db().cursor()
    consulta= 'SELECT idactions FROM actions WHERE title LIKE "%pandora%"' 
    cur.execute(consulta)
    act=cur.fetchone()

    consulta3= 'SELECT iduser FROM usuarios WHERE email=%s'
    cur.execute(consulta3, session.get("email"))
    id = cur.fetchone()
                    
    cur.execute('INSERT INTO user_actions (id_user, action) VALUES (%s,%s)', (id,act))
    mysql.get_db().commit()
    cur.close()
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
    variable_env5 = {os.getenv("GRUPO_AA")}
    id_str = " ".join(variable_env5)
    print(id_str)
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/subsistemaAA.html", id5=id_str)
    elif(perfil != 'Administrador'):
        return render_template("noadmin/subsistemaAA.html", id5=id_str)
@app.route('/subsistemaCM')
def subsistemaCM():
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/subsistemaCM.html")
    elif(perfil != 'Administrador'):
        return render_template("noadmin/subsistemaCM.html")
@app.route('/subsistemaGF')
def subsistemaGF():
    variable_env8 = {os.getenv("GRUPO_GF")}
    id_str = " ".join(variable_env8)
    print(id_str)
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/subsistemaGF.html", id8=id_str)
    elif(perfil != 'Administrador'):
        return render_template("noadmin/subsistemaGF.html", id8=id_str)
@app.route('/subsistemaO')
def subsistemaO():
    variable_env6 = {os.getenv("GRUPO_O")}
    id_str = " ".join(variable_env6)
    print(id_str)
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/subsistemaO.html", id6=id_str)
    elif(perfil != 'Administrador'):
        return render_template("noadmin/subsistemaO.html")
@app.route('/subsistemaCO')
def subsistemaCO():
    variable_env7 = {os.getenv("GRUPO_CO")}
    id_str = " ".join(variable_env7)
    print(id_str)
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/subsistemaCO.html", id7=id_str )
    elif(perfil != 'Administrador'):
        return render_template("noadmin/subsistemaCO.html")

@app.route('/subsistemaconfAA')
def subsistemaconfAA():
    return ("Hola")
@app.route('/subsistemaconfBD')
def subsistemaconfBD():
    return render_template("admin/subsistemaconfBD.html")

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
'''
@app.route('/envio')
def envio():
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
    try:
        connUser='root'
        connHost='192.168.1.159'
        connPath="/root"
        scp = subprocess.Popen(["scp", "private.pem", "{}@{}:{}".format(connUser, connHost, connPath)])
        #print (open("localpath").read())
    except subprocess.CalledProcessError:
        print('ERROR: Connection to host failed!')
    return('hola')'''
@app.route('/pruebaclave')
def pruebaclave():
    #Genero llaves con un random
    clave_random = Crypto.Random.new().read
    private_key = RSA.generate(1024, clave_random)
    public_key = private_key.publickey()
    #Exporto las llaves para convertirlas a utf-8
    private_key=private_key.export_key(format='PEM')
    public_key=public_key.export_key(format='PEM')

    file_out = open("id_rsa", "wb")
    file_out.write(private_key)
    file_out.close()
    file_out = open("id_rsa.pub", "wb")
    file_out.write(public_key)
    file_out.close()
    try:
        connUser='root'
        connHost='192.168.1.163'
        connPath="root/.ssh"
        scp = subprocess.Popen(["scp", "id_rsa", "{}@{}:{}".format(connUser, connHost, connPath)])
        #print (open("localpath").read())
    except subprocess.CalledProcessError:
        print('ERROR: Connection to host failed!')
    return("hola")

@app.route('/clavessensores')
def clavessensores():
    path = "M:\proyecto\id_rsa.pub"
    return send_file(path, as_attachment=True) 
@app.route('/clavessubsistemas')
def clavessubsistemas():
    return render_template("admin/clavessubsistemas.html") 

@app.route('/descargas')#novale
def descargas():  
    path = "M:\proyecto\public.pem"
    try:
        return send_file(path, as_attachment=True), redirect(url_for("clavessensores"))
    except:
        print("Error")
    return("hello")
@app.route('/sendkey')#novale
def sendkey():  
    path = "M:\proyecto\public.pem"
    return send_file(path, as_attachment=True)