from app import app
from flask import Flask, render_template, url_for, request, redirect, flash, session
from flaskext.mysql import MySQL
#from flask_mysqldb import MySQL
import bcrypt

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
        return render_template("index.html")
    else:
        return render_template("login.html")

@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/registro', methods = ["GET", "POST"])
def registro():
    
    if request.method == "GET":
        if 'nombre' in session:
           return render_template("registro.html")
        else:
            return "No puedes registrar usuarios si no eres el admin de la plataforma"
        #return render_template("registro.html")
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
        consulta='SELECT nombre, email, perfil, password FROM usuarios where email =%s'
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
        consulta='SELECT nombre, email, perfil, password FROM usuarios where email =%s'
        cur.execute(consulta, [email])
        row = cur.fetchone()
        cur.close()

        if (row != None):
            password_encriptada_encode = row[3].encode()
            if (bcrypt.checkpw(password_encode, password_encriptada_encode)):
                session["nombre"] = row[0]
                session["email"] = row[1]
                session["perfil"] = row[2]
                return redirect(url_for("index"))
            else:
                flash("La contraseña introducida es incorrecta")
                return(render_template("login.html"))
        if( row == None):
            flash("El correo electrónico introducido es incorrecto")
            return (render_template("login.html"))

@app.route('/usuarios_registrados')
def usuarios_registrados():
    cur = mysql.get_db().cursor()
    cur.execute('SELECT * FROM usuarios')
    data = cur.fetchall()
    perfil = session.get('perfil')
    print(perfil)
    if (perfil == 'Administrador'):
        return render_template("usuariosregistrados.html", contacts = data)
    else:
        return render_template("noadmin/usuariosregistrados.html", contacts = data)

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
    return render_template('usuarioseditados.html', contact = data[0])

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
    return render_template("perfiles.html")