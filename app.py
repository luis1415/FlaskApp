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

app = Flask(__name__)
# app.secret_key = 'llavesecreta123'
# Se debe llamar la funcion aqui, y se guarda en una variable
Articles = articles()
config = mysql_conf()

# configuracion de MySQL
app.config['MYSQL_HOST'] = config['host']
app.config['MYSQL_USER'] = config['user']
app.config['MYSQL_PASSWORD'] = config['password']
app.config['MYSQL_DB'] = config['db']
app.config['MYSQL_CURSORCLASS'] = config['class']

# Inicializar MySQL
mysql = MySQL(app)


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
                return redirect(url_for('dashboard'))
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

    print(letras, frecuencias)
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
