from typing import Any
from app import app
from flask import Flask, render_template, url_for, request, redirect, flash, session, make_response
from flaskext.mysql import MySQL
# from flask_mysqldb import MySQL
import bcrypt
import os
import Crypto
import paramiko  # automatizar tareas con SSH
from Crypto.PublicKey import RSA
import subprocess 
from flask.helpers import send_file

# ------------------Inicializo BBDD------------------------
# Config de la BBDD
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Mysql1234'
app.config['MYSQL_DATABASE_DB'] = 'flask_usuarios'
mysql = MySQL(app)

# Cómo va protegida la sesión
app.secret_key = 'mysecretkey'

# Encrypt config
salt = bcrypt.gensalt()

# PANDORA CONFIG
PANDORA_HOST = '192.168.1.180'
PANDORA_USER = 'root'

#RIESGO DINÁMICO CONFIG
RISK_HOST = '192.168.1.144'


@app.route('/')
def main():
    if 'nombre' in session:
        perfil = session.get('perfil')
        if (perfil == 'Administrador'):
            return render_template("admin/index.html", RISK_HOST=RISK_HOST)
        elif(perfil != 'Administrador'):
            return render_template("noadmin/index.html", RISK_HOST=RISK_HOST)
    else:
        return render_template("login.html")


@app.route('/index')
def index():
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/index.html", RISK_HOST=RISK_HOST)
    else:
        return render_template("noadmin/index.html", RISK_HOST=RISK_HOST)

# ------------------------------ADMINISTRACIÓN--------------------------------------------------------


@app.route('/registro', methods=["GET", "POST"])
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
            return redirect(url_for("registro"))
        if email == "":
            flash("Debe indicar su correo electrónico")
            return redirect(url_for("registro"))
        if perfil == "Noseleccionado":
            flash("Debe indicar su tipo de perfil")
            return redirect(url_for("registro"))
        if password == "":
            flash("Debe indicar su contraseña")
            return redirect(url_for("registro"))
        if password == passwordconf:
            password_encode = password.encode("utf-8")
            password_encriptada = bcrypt.hashpw(password_encode, salt)

            cur = mysql.get_db().cursor()
            consulta = 'SELECT  iduser, nombre, email, perfil, password FROM usuarios where email =%s'
            cur.execute(consulta, [email])
            row = cur.fetchone()
            if row == None:
                cur.execute('INSERT INTO usuarios (nombre, email, perfil, password) VALUES (%s,%s,%s,%s)',
                            (nombre, email, perfil, password_encriptada))

                consulta2 = 'SELECT idactions FROM actions WHERE title LIKE "%registro%"'
                cur.execute(consulta2)
                act = cur.fetchone()

                consulta3 = 'SELECT iduser FROM usuarios WHERE email=%s'
                cur.execute(consulta3, [email])
                id = cur.fetchone()

                cur.execute(
                    'INSERT INTO user_actions (id_user, action) VALUES (%s,%s)', (id, act))
                mysql.get_db().commit()
                cur.close()

            else:
                flash("Ya existe un usuario con dicho correo electrónico")
                return redirect(url_for("registro"))
        else:
            flash("Las contraseñas no coinciden")
            return redirect(url_for("registro"))

    return redirect(url_for('index'))


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form["emailLogin"]
        password = request.form["passwordLogin"]
        password_encode = password.encode("utf-8")

        if email == "":
            flash("Debe indicar su correo electrónico")
            return redirect(url_for("login"))
        if password == "":
            flash("Debe indicar su contraseña")
            return redirect(url_for("login"))

        cur = mysql.get_db().cursor()
        consulta = 'SELECT iduser, nombre, email, perfil, password FROM usuarios where email =%s'
        cur.execute(consulta, [email])
        row = cur.fetchone()

        if (row != None):
            password_encriptada_encode = row[4].encode()
            if (bcrypt.checkpw(password_encode, password_encriptada_encode)):
                session["id"] = row[0]
                session["nombre"] = row[1]
                session["email"] = row[2]
                session["perfil"] = row[3]

                consulta2 = 'SELECT idactions FROM actions WHERE title LIKE "%login%"'
                cur.execute(consulta2)
                act = cur.fetchone()

                consulta3 = 'SELECT iduser FROM usuarios WHERE email=%s'
                cur.execute(consulta3, [email])
                id = cur.fetchone()

                cur.execute(
                    'INSERT INTO user_actions (id_user, action) VALUES (%s,%s)', (id, act))
                mysql.get_db().commit()
                cur.close()
                return redirect(url_for("main"))
            else:
                flash("Las credenciales introducidas son incorrectas")
                return(render_template("login.html"))
        if(row == None):
            flash("Las credenciales introducidas son incorrectas")
            return (render_template("login.html"))


@app.route('/usuarios_registrados')
def usuarios_registrados():
    cur = mysql.get_db().cursor()
    cur.execute('SELECT * FROM usuarios')
    data = cur.fetchall()
    return render_template("admin/usuariosregistrados.html", contacts=data)


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
    consulta = ('SELECT * FROM usuarios WHERE email= %s')
    cursor.execute(consulta, [email])
    data = cursor.fetchall()
    return render_template('admin/usuarioseditados.html', contact=data[0])


@app.route('/update/<string:email>', methods=['POST'])
def update_contact(email):
    if request.method == 'POST':
        nombre = request.form['nombreActualizado']
        email = request.form['emailActualizado']
        perfil = request.form['perfilActualizado']

        cursor = mysql.get_db().cursor()
        cursor.execute("""
            UPDATE usuarios
            SET nombre= '{0}',
                email = '{1}',
                perfil = '{2}'
            WHERE email = '{1}'"""
                       .format(nombre, email, perfil))
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
    return render_template("admin/acciones.html", datos=datos)

# -------------------------------------------GESTIÓN-----------------------------------------------------------------
# -----------------------SENSORES------------------------------------------------------------------------------------


@app.route('/sensoresWF')
def sensoresWF():
    variable_env1 = {os.getenv("GRUPO_WIFI")}
    id_str = " ".join(variable_env1)
    # id_str="17"
    print(id_str)
    cur = mysql.get_db().cursor()
    consulta = 'SELECT idactions FROM actions WHERE title LIKE "%pandora%"'
    cur.execute(consulta)
    act = cur.fetchone()

    consulta3 = 'SELECT iduser FROM usuarios WHERE email=%s'
    cur.execute(consulta3, session.get("email"))
    id = cur.fetchone()

    cur.execute(
        'INSERT INTO user_actions (id_user, action) VALUES (%s,%s)', (id, act))
    mysql.get_db().commit()
    cur.close()
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/sensoresWF.html", idwifi=id_str, PANDORA_HOST=PANDORA_HOST)
    elif(perfil != 'Administrador'):
        return render_template("noadmin/sensoresWF.html", idwifi=id_str, PANDORA_HOST=PANDORA_HOST)


@app.route('/sensoresBT')
def sensoresBT():
    variable_env2 = {os.getenv("GRUPO_BLUETOOTH")}
    idstr = " ".join(variable_env2)
    cur = mysql.get_db().cursor()
    consulta = 'SELECT idactions FROM actions WHERE title LIKE "%pandora%"'
    cur.execute(consulta)
    act = cur.fetchone()

    consulta3 = 'SELECT iduser FROM usuarios WHERE email=%s'
    cur.execute(consulta3, session.get("email"))
    id = cur.fetchone()

    cur.execute(
        'INSERT INTO user_actions (id_user, action) VALUES (%s,%s)', (id, act))
    mysql.get_db().commit()
    cur.close()
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/sensoresBT.html", id2=idstr, PANDORA_HOST=PANDORA_HOST)
    elif(perfil != 'Administrador'):
        return render_template("noadmin/sensoresBT.html", id2=idstr, PANDORA_HOST=PANDORA_HOST)


@app.route('/sensoresRF')
def sensoresRF():
    variable_env3 = {os.getenv("GRUPO_RF")}
    idstr = " ".join(variable_env3)
    print(idstr)
    cur = mysql.get_db().cursor()
    consulta = 'SELECT idactions FROM actions WHERE title LIKE "%pandora%"'
    cur.execute(consulta)
    act = cur.fetchone()

    consulta3 = 'SELECT iduser FROM usuarios WHERE email=%s'
    cur.execute(consulta3, session.get("email"))
    id = cur.fetchone()

    cur.execute(
        'INSERT INTO user_actions (id_user, action) VALUES (%s,%s)', (id, act))
    mysql.get_db().commit()
    cur.close()
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/sensoresRF.html", id3=idstr, PANDORA_HOST=PANDORA_HOST)
    elif(perfil != 'Administrador'):
        return render_template("noadmin/sensoresRF.html", id3=idstr, PANDORA_HOST=PANDORA_HOST)


@app.route('/sensoresRM')
def sensoresRM():
    variable_env4 = {os.getenv("GRUPO_RM")}
    idstr = " ".join(variable_env4)
    print(idstr)
    cur = mysql.get_db().cursor()
    consulta = 'SELECT idactions FROM actions WHERE title LIKE "%pandora%"'
    cur.execute(consulta)
    act = cur.fetchone()

    consulta3 = 'SELECT iduser FROM usuarios WHERE email=%s'
    cur.execute(consulta3, session.get("email"))
    id = cur.fetchone()

    cur.execute(
        'INSERT INTO user_actions (id_user, action) VALUES (%s,%s)', (id, act))
    mysql.get_db().commit()
    cur.close()
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/sensoresRM.html", id4=idstr, PANDORA_HOST=PANDORA_HOST)
    elif(perfil != 'Administrador'):
        return render_template("noadmin/sensoresRM.html", id4=idstr, PANDORA_HOST=PANDORA_HOST)


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
    consulta = ('SELECT * FROM sensores WHERE idsensores= %s')
    cursor.execute(consulta, [idsensores])
    sensor = cursor.fetchall()
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template('admin/sensoreseditados.html', sensores=sensor[0])
    elif(perfil != 'Administrador'):
        return render_template("noadmin/sensoreseditados.html", sensores=sensor[0])
    


@app.route('/update/sensores/<int:idsensores>', methods=['POST'])
def update_sensor(idsensores):
    if request.method == 'POST':
        nombre = request.form['nombreActualizado']
        tipo = request.form['tipoActualizado']
        mac = request.form['macActualizada']
        ip = request.form['ipActualizada']
        descripcion = request.form["descripcionActualizada"]

        cursor = mysql.get_db().cursor()
        cursor.execute("""
            UPDATE sensores
            SET nombre= '{1}',
                tipo = '{2}',
                mac = '{3}',
                ip = '{4}',
                descripcion = '{5}'
            WHERE idsensores = '{0}'"""
                       .format(idsensores, nombre, tipo, mac, ip, descripcion))
        mysql.get_db().commit()
        flash("Sensor actualizado satisfactoriamente")
        return redirect(url_for('sensores'))


@app.route('/registrosensores', methods=["GET", "POST"])
def registrosensores():
    if request.method == "GET":
        perfil = session.get('perfil')
        if (perfil == 'Administrador'):
            return render_template("admin/registrarsensor.html")
        elif(perfil != 'Administrador'):
            return render_template("noadmin/registrarsensor.html")
        
    else:
        nombre = request.form["nombreSensor"]
        tipo = request.form["tipoRegistro"]
        mac = request.form["macRegistro"]
        ip = request.form["ipRegistro"]
        descripcion = request.form["descripcionRegistro"]

        if nombre == "":
            flash("Debe indicar un nombre")
            return redirect(url_for("registrosensores"))
        if tipo == "Noseleccionado":
            flash("Debe indicar el tipo del sensor")
            return redirect(url_for("registrosensores"))
        if mac == "":
            flash("Debe indicar una dirección MAC")
            return redirect(url_for("registrosensores"))

        cur = mysql.get_db().cursor()
        consulta = 'SELECT  idsensores, nombre, tipo, mac, ip, descripcion FROM sensores WHERE mac=%s'
        cur.execute(consulta, [mac])
        row = cur.fetchone()
        if row == None:
            cur.execute('INSERT INTO sensores (nombre, tipo, mac, ip, descripcion) VALUES (%s,%s,%s,%s,%s)',
                        (nombre, tipo, mac, ip, descripcion))
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
        return render_template("admin/sensores.html", sensores=sensores)
    elif(perfil != 'Administrador'):
        return render_template("noadmin/sensores.html", sensores=sensores)


@app.route('/consolaPandora')
def consolaPandora():
    cur = mysql.get_db().cursor()
    consulta = 'SELECT idactions FROM actions WHERE title LIKE "%pandora%"'
    cur.execute(consulta)
    act = cur.fetchone()

    consulta3 = 'SELECT iduser FROM usuarios WHERE email=%s'
    cur.execute(consulta3, session.get("email"))
    id = cur.fetchone()

    cur.execute(
        'INSERT INTO user_actions (id_user, action) VALUES (%s,%s)', (id, act))
    mysql.get_db().commit()
    cur.close()
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/consolaPandora.html", PANDORA_HOST=PANDORA_HOST)
    elif(perfil != 'Administrador'):
        return render_template("noadmin/consolaPandora.html", PANDORA_HOST=PANDORA_HOST)

# -----------------------SUBSISTEMAS------------------------------------------------------------------------------------


@app.route('/subsistemaBD')
def subsistemaBD():
    variable_env9 = {os.getenv("GRUPO_GF")}
    id_str = " ".join(variable_env9)
    print(id_str)
    perfil = session.get('perfil')
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/subsistemaBD.html", id9=id_str, PANDORA_HOST=PANDORA_HOST)
    elif(perfil != 'Administrador'):
        return render_template("noadmin/subsistemaBD.html", id9=id_str, PANDORA_HOST=PANDORA_HOST)


@app.route('/subsistemaAA')
def subsistemaAA():
    variable_env5 = {os.getenv("GRUPO_AA")}
    id_str = " ".join(variable_env5)
    print(id_str)
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/subsistemaAA.html", id5=id_str, PANDORA_HOST=PANDORA_HOST)
    elif(perfil != 'Administrador'):
        return render_template("noadmin/subsistemaAA.html", id5=id_str, PANDORA_HOST=PANDORA_HOST)



@app.route('/subsistemaGF')
def subsistemaGF():
    variable_env8 = {os.getenv("GRUPO_GF")}
    id_str = " ".join(variable_env8)
    print(id_str)
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/subsistemaGF.html", id8=id_str, PANDORA_HOST=PANDORA_HOST)
    elif(perfil != 'Administrador'):
        return render_template("noadmin/subsistemaGF.html", id8=id_str, PANDORA_HOST=PANDORA_HOST)


@app.route('/subsistemaO')
def subsistemaO():
    variable_env6 = {os.getenv("GRUPO_O")}
    id_str = " ".join(variable_env6)
    print(id_str)
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/subsistemaO.html", id6=id_str, PANDORA_HOST=PANDORA_HOST)
    elif(perfil != 'Administrador'):
        return render_template("noadmin/subsistemaO.html", id6=id_str, PANDORA_HOST=PANDORA_HOST)


@app.route('/subsistemaCO')
def subsistemaCO():
    variable_env7 = {os.getenv("GRUPO_CO")}
    id_str = " ".join(variable_env7)
    print(id_str)
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/subsistemaCO.html", id7=id_str, PANDORA_HOST=PANDORA_HOST)
    elif(perfil != 'Administrador'):
        return render_template("noadmin/subsistemaCO.html", id7=id_str, PANDORA_HOST=PANDORA_HOST)
# -------------------------------------------GONFIGURACIÓN SUBSISTEMAS-----------------------------------------------------------------

#--------------------------------------------CONFIGURACIÓN AA--------------------------------------------------------------------------
@app.route('/subsistemaconfAA')
def subsistemaconfAA(): 
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/subsistemaconfAA.html")
    elif(perfil != 'Administrador'):
        return render_template("noadmin/subsistemaconfAA.html")
    
@app.route('/subsistemaconfsensores', methods=["POST"])
def subsistemaconfsensores():
    usuario = request.form["usuario"]
    ip = request.form["ip"]
    action= request.form["action"]
    if usuario == "":
        flash("Debe indicar un usuario")
        return redirect(url_for("subsistemaconfGF"))
    if ip == "":
        flash("Debe indicar una dirección IP")
        return redirect(url_for("subsistemaconfGF"))
    if action == "defect":
        flash("Por favor seleccione una acción")
        return redirect(url_for("subsistemaconfGF"))
    if action == "startwifi":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/launch_spark_WF.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "stopwifi":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/stop_spark_WF.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "startrm":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/launch_spark_RM.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "stoprm":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/stop_spark_RM.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "startrf":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/launch_spark_RF.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "stoprf":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/stop_spark_RF.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "startfw":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/launch_spark_FW.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "stopfw":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/stop_spark_FW.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "startbt":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/launch_spark_BT.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "stopbt":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/stop_spark_BT.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "starttids":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/launch_spark_TIDS.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "stoptids":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/stop_spark_TIDS.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])


@app.route('/subsistemaconfUBA', methods=["POST"])
def subsistemaconfUBA():
    usuario = request.form["usuario"]
    ip = request.form["ip"]
    action = request.form["action"]
    if usuario == "":
        flash("Debe indicar un usuario")
        return redirect(url_for("subsistemaconfAA"))
    if ip == "":
        flash("Debe indicar una dirección IP")
        return redirect(url_for("subsistemaconfAA"))
    if action == "defect":
        flash("Por favor seleccione una acción")
        return redirect(url_for("subsistemaconfAA"))
    if action == "startubaall":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/launch_spark_UBA_all.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "stopubaall":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/stop_spark_UBA_all.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "startuba1":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/launch_spark_UBA_mod1.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "stopuba1":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/stop_spark_UBA_mod1.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "startuba2":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/launch_spark_UBA_mod2.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "stopuba2":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/stop_spark_UBA_mod2.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "startuba3":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/launch_spark_UBA_mod3.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "stopuba3":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/stop_spark_UBA_mod3.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "startuba4":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/launch_spark_UBA_mod4.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "stopuba4":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/stop_spark_UBA_mod4.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "startuba5":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/launch_spark_UBA_mod5.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "stopuba5":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/stop_spark_UBA_mod5.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "startuba6":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/launch_spark_UBA_mod6.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "stopuba6":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/stop_spark_UBA_mod6.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "startuba7":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/launch_spark_UBA_mod7.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "stopuba7":
        scp = subprocess.Popen(
            f"ssh {usuario}@{ip} /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/stop_spark_UBA_mod7.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
#--------------------------------------------CONFIGURACIÓN GF--------------------------------------------------------------------------
@app.route('/subsistemaconfGF',methods=["GET", "POST"])
def subsistemaconfGF():
    if request.method == "GET":
        perfil = session.get('perfil')
        if (perfil == 'Administrador'):
            return render_template("admin/subsistemaconfGF.html")
        elif(perfil != 'Administrador'):
            return render_template("noadmin/subsistemaconfGF.html")
    else:
        usuariokafka = request.form["usuariokafka"]
        ipkafka = request.form["ipkafka"]
        accionkafka = request.form["accionkafka"]

        if (usuariokafka) == "":
            flash("Debe indicar un usuario")
            return redirect(url_for("subsistemaconfGF"))
        if (ipkafka) == "":
            flash("Debe indicar una dirección IP")
            return redirect(url_for("subsistemaconfGF"))
        if accionkafka == "start":
            scp = subprocess.Popen(
                f"ssh {usuariokafka}@{ipkafka} /home/vagrant/kafka/bin/kafka-server-start.sh / home/vagrant/kafka/config/server.properties", stdout=subprocess.PIPE)
            return (scp.communicate()[0])
        if accionkafka == "stop":
           scp = subprocess.Popen(
               f"ssh {usuariokafka}@{ipkafka} bash /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/stop_kafka.sh", stdout=subprocess.PIPE)
           return (scp.communicate()[0])

     
    #return render_template("admin/subsistemaconfGF.html")
@app.route('/zookeper', methods=["POST"])
def zookeeper():
    usuariozookeper = request.form["usuariozookeper"]
    ipzookeper = request.form["ipzookeper"]
    accionzookeper = request.form["accionzookeper"]
    if (usuariozookeper) == "":
        flash("Debe indicar un usuario")
        return redirect(url_for("subsistemaconfGF"))
    if (ipzookeper) == "":
        flash("Debe indicar una dirección IP")
        return redirect(url_for("subsistemaconfGF"))
    if accionzookeper == "start":
        scp = subprocess.Popen(
            f"ssh {usuariozookeper}@{ipzookeper} /home/vagrant/kafka/bin/zookeeper-server-start.sh / home/vagrant/kafka/config/zookeeper.properties", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if accionzookeper == "stop":
        scp = subprocess.Popen(
            f"ssh {usuariozookeper}@{ipzookeper} bash /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/stop_zookeeper.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    
    return redirect(url_for("subsistemasconfGF"))

@app.route('/listtopics', methods=["POST"])
def listartopics():
    usuariotopics = request.form["usuariotopics"]
    iptopics = request.form["iptopics"]
    if (usuariotopics) == "":
        flash("Debe indicar un usuario")
        return redirect(url_for("subsistemaconfGF"))
    if (iptopics) == "":
        flash("Debe indicar una dirección IP")
        return redirect(url_for("subsistemaconfGF"))
    scp = subprocess.Popen(
        f"ssh {usuariotopics}@{iptopics} bash /home/vagrant/scripts_core_plica/pandora_fms_agente_vagrant/check_list_topics.sh", stdout=subprocess.PIPE)
    return (scp.communicate()[0])


@app.route('/createtopic', methods=["POST"])
def createtopic():
    usuariocrtopics = request.form["usuariocrtopics"]
    ipcrtopics = request.form["ipcrtopics"]
    broker_ip = request.form["broker_ip"]
    puerto = request.form["puerto"]
    valor1 = request.form["valor1"]
    valor2 = request.form["valor2"]
    topicname = request.form["topicname"]
    if (usuariocrtopics) == "":
        flash("Debe indicar un usuario")
        return redirect(url_for("subsistemaconfGF"))
    if (ipcrtopics) == "":
        flash("Debe indicar una dirección IP")
        return redirect(url_for("subsistemaconfGF"))
    if (broker_ip) == "":
        flash("Debe indicar la dirección IP del Broker")
        return redirect(url_for("subsistemaconfGF"))
    if (puerto) == "":
        flash("Debe indicar un puerto")
        return redirect(url_for("subsistemaconfGF"))
    if (valor1 or valor2) == "":
        flash("Debe indicar un valor")
        return redirect(url_for("subsistemaconfGF"))
    if (topicname) == "":
        flash("Debe indicar el nombre del TOPIC a crear")
        return redirect(url_for("subsistemaconfGF"))

    scp = subprocess.Popen(
        f'ssh {usuariocrtopics}@{ipcrtopics} /home/vagrant/kafka/bin/kafka-topics.sh --create --bootstrap-server={broker_ip}:${puerto} --command-config=/opt/kafka/config/producer_ssl.properties --replication-factor {valor1} --partitions {valor2} --topic "{topicname}"  --config retention.ms=5000', stdout=subprocess.PIPE)
    return (scp.communicate()[0])


@app.route('/rmtopic', methods=["POST"])
def rmtopic():
    usuariormtopics = request.form["usuariormtopics"]
    iprmtopics = request.form["iprmtopics"]
    brokerrm_ip = request.form["brokerrm_ip"]
    topicrmname = request.form["topicrmname"]

    if usuariormtopics == "":
        flash("Debe indicar un usuario")
        return redirect(url_for("subsistemaconfGF"))
    if iprmtopics == "":
        flash("Debe indicar una dirección IP")
        return redirect(url_for("subsistemaconfGF"))
    if (brokerrm_ip) == "":
        flash("Debe indicar la dirección IP del broker")
        return redirect(url_for("subsistemaconfGF"))
    if (topicrmname) == "":
        flash("Debe indicar el nombre del TOPIC a eliminar")
        return redirect(url_for("subsistemaconfGF"))
    scp = subprocess.Popen(
        f'ssh {usuariormtopics}@{iprmtopics} /home/vagrant/kafka/bin/kafka-topics.sh --delete --zookeeper {brokerrm_ip}:2181 --topic "{topicrmname}"', stdout=subprocess.PIPE)
    return (scp.communicate()[0])
#--------------------------------------------CONFIGURACIÓN O--------------------------------------------------------------------------
@app.route('/subsistemaconfO')
def subsistemaconfO():
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/subsistemaconfO.html")
    elif(perfil != 'Administrador'):
        return render_template("noadmin/subsistemaconfO.html")
    


@app.route('/ontologias', methods=["POST"])
def ontologias():
    usuario = request.form["usuario"]
    ip = request.form["ip"]
    action = request.form["action"]
    if usuario == "":
        flash("Debe indicar un usuario")
        return redirect(url_for("subsistemaconfO"))
    if ip == "":
        flash("Debe indicar una dirección IP")
        return redirect(url_for("subsistemaconfO"))
    if action == "defect":
        flash("Por favor, seleccione una acción")
        return redirect(url_for("subsistemaconfO"))
    if action == "start":
        scp = subprocess.Popen(
            f"ssh {PANDORA_USER}@{PANDORA_HOST} ./bash_prueba.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if action == "stop":
        scp = subprocess.Popen(
            f"ssh {PANDORA_USER}@{PANDORA_HOST} ./bash_prueba.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])


@app.route('/fuseki', methods=["POST"])
def fuseki():
    usuariofuseki = request.form["usuariofuseki"]
    ipfuseki = request.form["ipfuseki"]
    actionfuseki = request.form["actionfuseki"]
    if usuariofuseki == "":
        flash("Debe indicar un usuario")
        return redirect(url_for("subsistemaconfO"))
    if ipfuseki == "":
        flash("Debe indicar una dirección IP")
        return redirect(url_for("subsistemaconfO"))
    if actionfuseki == "defect":
        flash("Por favor, seleccione una acción")
        return redirect(url_for("subsistemaconfO"))
    if actionfuseki == "start":
        scp = subprocess.Popen(
            f"ssh {PANDORA_USER}@{PANDORA_HOST} ./bash_prueba.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
    if actionfuseki == "stop":
        scp = subprocess.Popen(
            f"ssh {PANDORA_USER}@{PANDORA_HOST} ./bash_prueba.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])
#--------------------------------------------CONFIGURACIÓN CO--------------------------------------------------------------------------
@app.route('/subsistemaconfCO')
def subsistemaconfCO():
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/subsistemaconfCO.html")
    elif(perfil != 'Administrador'):
        return render_template("noadmin/subsistemaconfCO.html")

@app.route('/correlacion', methods=["POST"])
def correlacion():
    usuario = request.form["usuario"]
    ip = request.form["ip"]
    action = request.form["action"]
    if usuario == "":
        flash("Debe indicar un usuario")
        return redirect(url_for("subsistemaconfCO"))
    if ip == "":
        flash("Debe indicar una dirección IP")
        return redirect(url_for("subsistemaconfCO"))
    if action == "defect":
        flash("Por favor, seleccione una acción")
        return redirect(url_for("subsistemaconfCO"))
    if action == "start":
        scp = subprocess.Popen(
            f"ssh {PANDORA_USER}@{PANDORA_HOST} ./bash_prueba.sh", stdout=subprocess.PIPE)
        flash("Subsistema arrancado con éxito")
        return redirect(url_for("subsistemaconfCO"))
        #return (scp.communicate()[0])
    if action == "stop":
        scp = subprocess.Popen(
            f"ssh {PANDORA_USER}@{PANDORA_HOST} ./bash_prueba.sh", stdout=subprocess.PIPE)
        return (scp.communicate()[0])



@app.route('/salir')
def salir():
    session.clear()
    return redirect(url_for("main"))

# -------------------------------------------CLAVES-----------------------------------------------------------------
def new_keys_generation(type): 

    random_generator = Crypto.Random.new().read
    private_key = RSA.generate(1024, random_generator)
    public_key = private_key.publickey()

    private_key = private_key.export_key()
    public_key = public_key.export_key()

    private_key_PATH = f"keystore/{type}_private"
    public_key_PATH = f"keystore/{type}_public.pub"

    file_out = open(private_key_PATH, "wb")
    file_out.write(private_key)
    file_out.close()

    file_out = open(public_key_PATH, "wb")
    file_out.write(public_key)
    file_out.close()

    try:
        connPath = "/root/.ssh"
        scp = subprocess.Popen(
            ["scp", private_key_PATH, "{}@{}:{}".format(PANDORA_USER, PANDORA_HOST, connPath)])
        scp.wait()
        os.unlink(private_key_PATH)
    except subprocess.CalledProcessError:
        print('ERROR: Connection to host failed!')
    return (1)


@app.route('/clavessensores')
def clavessensores():
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/clavessensores.html")
    elif(perfil != 'Administrador'):
        return render_template("noadmin/clavessensores.html")


@app.route('/clavessubsistemas')
def clavesubsistemas():
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/clavessubsistemas.html")
    elif(perfil != 'Administrador'):
        return render_template("noadmin/clavessubsistemas.html")

@app.route('/botonsensores')
def botonsensores():
    if not (os.path.isfile("../keystore/sensores_public.pub")):
        new_keys_generation('sensores')

    path = "..\keystore\sensores_public.pub"
    return send_file(path, as_attachment=True)


@app.route('/botonsubsistemas')
def botonsubsistemas():
    if not (os.path.isfile("../keystore/subsistemas_public.pub")):
        new_keys_generation('subsistemas')

    path = "..\keystore\subsistemas_public.pub"
    return send_file(path, as_attachment=True)


@app.route('/a')
def a():
    scp = subprocess.Popen(
        f"ssh {PANDORA_USER}@{PANDORA_HOST} ./bash_prueba.sh", stdout=subprocess.PIPE)
    return (scp.communicate()[0])

#--------------------------------------------VISUALIZACION--------------------------------------------------------------------------


@app.route('/dynamicrisk')
def dynamicrisk():
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/riesgo.html", RISK_HOST=RISK_HOST)
    elif(perfil != 'Administrador'):
        return render_template("noadmin/riesgo.html", RISK_HOST=RISK_HOST)

@app.route('/dataquery')
def dataquery():
    perfil = session.get('perfil')
    if (perfil == 'Administrador'):
        return render_template("admin/data.html", RISK_HOST=RISK_HOST)
    elif(perfil != 'Administrador'):
        return render_template("noadmin/data.html", RISK_HOST=RISK_HOST)


@app.route('/filtrar?busqueda=crear_usuario')
def filtrar():
    perfil = session.get('perfil')
    busqueda = request.form["busqueda"]
    select = request.form["select"]
    if (perfil == 'Administrador'):
        if (busqueda == "usuarios_registrados"):
            return render_template("admin/usuariosregistrados.html")
        if (busqueda == "crear_usuario"):
            return render_template("admin/registroframe.html")
        else:
            return render_template("index.html")
    elif(perfil != 'Administrador'):
        return render_template("noadmin/data.html")
