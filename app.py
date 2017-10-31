from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import articles
from config import mysql_conf
from wtforms.fields.html5 import EmailField
from flask_mysqldb import MySQL
from wtforms import Form, StringField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import pandas as pd
import json
import MySQLdb
import datetime

app = Flask(__name__)
# Se debe llamar la funcion aqui, y se guarda en una variable
Articles = articles()
config = mysql_conf()[0]

# configuracion de MySQL
app.config['MYSQL_HOST'] = config['host']
app.config['MYSQL_USER'] = config['user']
app.config['MYSQL_PASSWORD'] = config['password']
app.config['MYSQL_DB'] = config['db']
app.config['MYSQL_CURSORCLASS'] = config['class']

# Inicializar MySQL
mysql = MySQL(app)


# css bootstrap
def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)


app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string


def fechas_json(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/articles')
def articles():
    return render_template('articles.html', articles=Articles)


@app.route('/article/<string:id_>/')
def article(id_):
    articulo = Articles[int(id_) - 1]
    return render_template('article.html', articulo=articulo)


class MyForm(Form):
    name = StringField('Nombre', validators=[validators.data_required(message="Nombre es un campo requerido")])
    username = StringField('Username', validators=[validators.Length(min=1, max=50)])
    email = EmailField('E-mail', validators=[validators.Length(min=6, max=50)])
    password = PasswordField('Password', validators=[validators.Length(min=1, max=50),
                                                     validators.DataRequired(message='Debe ingresar un password'),
                                                     validators.equal_to('confirm', message='passwords no coinciden')
                                                     ])
    confirm = PasswordField('Confirmar Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = MyForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # se crea el cursor
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO users(name, email, username, password) VALUES (%s, %s, %s, %s)", (name, email, username,
                                                                                           password))
        # commit a la base de datos
        mysql.connection.commit()

        # cerrar el cursor
        cur.close()

        # mensajes en flask se usa flash, para eso se agrega en includes los mensajes
        flash('Registrado', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/historia', methods=['GET', 'POST'])
def historia_clinica():
    if request.method == 'POST':
        data = request.form
        data2 = dict(
            (key, request.form.getlist(key) if len(request.form.getlist(key)) > 1 else request.form.getlist(key)[0]) for
            key in request.form.keys())

        conn = MySQLdb.connect(host=config['host'], port=config['port'], user=config['user'],
                               passwd=config['password'],
                               db=config['db'])
        cursor = conn.cursor()

        columnas = ""
        for i in range(len(data2.keys())):
            columnas += data2.keys()[i]
            if i < len(data2.keys()) - 1:
                columnas += ', '
        print columnas

        valores = ""
        for i in range(len(data2.values())):
            valores += "\'" + str(data2.values()[i]) + "\'"
            if i < len(data2.values()) - 1:
                valores += ', '
        print valores

        query = "INSERT INTO historia ({}) VALUES ({})".format(columnas, valores)
        flash('Guardado Correctamente !!!', 'success')
        cursor.execute(query)
        conn.commit()
        cursor.close()
    fecha = datetime.datetime.today()
    return render_template('historia_clinica.html', fecha=fecha)


@app.route('/mostrar_historias', methods=['GET'])
def mostrar_historias():
    conn = MySQLdb.connect(host=config['host'], port=config['port'], user=config['user'],
                           passwd=config['password'],
                           db=config['db'])
    cursor = conn.cursor()
    query = "SELECT * FROM historia"
    try:
        cursor.execute(query)
        data = cursor.fetchall()
        # data = list(data)
        # data = json.dumps(data, default=fechas_json).encode('utf8')
        # se cierra el cursor
        cursor.close()
    except:
        data = {'respuesta': 500}
    conn.close()
    return render_template('mostrar_historias.html', data=data)


@app.route('/eliminar_historia/<id>', methods=['GET', 'POST'])
def eliminar_historias(id):
    conn = MySQLdb.connect(host=config['host'], port=config['port'], user=config['user'],
                           passwd=config['password'],
                           db=config['db'])
    cursor = conn.cursor()
    query = "DELETE FROM historia WHERE id_hc = {}".format(id)
    try:
        cursor.execute(query)
        conn.commit()
        query = "SELECT id_hc, nombre, apellido, cedula, ciudad, fecha_nacimiento FROM historia"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
    except:
        data = {'respuesta': 500}
    conn.close()
    flash('Eliminado', 'danger')
    return render_template('mostrar_historias.html', data=data)


@app.route('/editar_historias/<id>', methods=['GET', 'POST'])
def editar_historias(id):
    conn = MySQLdb.connect(host=config['host'], port=config['port'], user=config['user'],
                           passwd=config['password'],
                           db=config['db'])
    cursor = conn.cursor()
    try:
        query = "SELECT * FROM historia WHERE id_hc = {}".format(id)
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
    except:
        data = {'respuesta': 500}
    conn.close()
    return render_template('editar_historias.html', data=data)


@app.route('/guardar_historias', methods=['POST'])
def guardar_historias():
    """
    Esta funcion guarda las historias actualizandolas.
    :return: 
    """
    data = dict(
        (key, request.form.getlist(key) if len(request.form.getlist(key)) > 1 else request.form.getlist(key)[0]) for
        key in request.form.keys())

    # se construye el update
    query = "UPDATE historia SET "
    for key, value in data.iteritems():
        query += str(key) + " = " + "\'" + str(value) + "\'" + ", "
    query = query[:-2]
    query += " WHERE id_hc = {}".format(data['codigo'])
    print(query)

    conn = MySQLdb.connect(host=config['host'], port=config['port'], user=config['user'],
                           passwd=config['password'],
                           db=config['db'])
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        cursor.close()
    except:
        data = {'respuesta': 500}
    conn.close()

    return render_template('home.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # obtenemos los campos del formulario
        username = request.form['username']
        password_candidate = request.form['password']

        # se crea un cursor
        cur = mysql.connection.cursor()

        # se hace la consulta
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            data = cur.fetchone()
            password = data['password']

            # se comparan los passwords
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username

                flash('Login Correcto', 'success')
                return redirect(url_for('index'))
            else:
                error = 'Password incorrecta'
                return render_template('login.html', error=error)

            # se cierra el cursor
            cur.close()

        else:
            error = 'No existe el usuario'
            return render_template('login.html', error=error)

    return render_template('login.html')


# decorador para impedir que entren a dashboard sin loguear
def requires_logged(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('No esta autorizado, Por favor haga Login', 'info')
            return redirect(url_for('login'))

    return wrap


# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@requires_logged
def dashboard():
    # se crea un cursor
    cur = mysql.connection.cursor()

    # se hace la consulta
    result = cur.execute("SELECT * FROM letter")
    data = cur.fetchall()
    # se cierra el cursor
    cur.close()

    letras = []
    frecuencias = []

    for i in data:
        letras.append(str(i['letra']))
        frecuencias.append(int(i['frec']))

    # se pasa a dataframe
    df = pd.DataFrame({
        "Letter": letras,
        "Freq": frecuencias
    })
    # se pasa a diccionario json
    d = [
        dict([
            (colname, row[i])
            for i, colname in enumerate(df.columns)
        ])
        for row in df.values
    ]
    print('dataframe----------------------')
    print(df)
    print('diccionario--------------------')
    print(d)
    print('json---------------------------')
    print(json.dumps(d))
    return render_template('dashboard.html', data=json.dumps(d), tabla=data)


@app.route('/logout')
def logout():
    session.clear()
    flash('Logout', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key = 'llavesecreta1234'
    app.run(debug=True)
