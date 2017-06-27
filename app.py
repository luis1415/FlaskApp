from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import articles
from wtforms.fields.html5 import EmailField
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)
# app.secret_key = 'llavesecreta123'
# Se debe llamar la funcion aqui, y se guarda en una variable
Articles = articles()

# configuracion de MySQL
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_example'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

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
    return render_template('article.html', id=id_)


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
                msg = 'Login Correcto'
                return render_template('home.html', msg=msg)
            else:
                error = 'Password incorrecta'
                return render_template('login.html', error=error)
        else:
            error = 'No existe el usuario'
            return render_template('login.html', error=error)

    return render_template('login.html')

if __name__ == '__main__':
    app.secret_key = 'llavesecreta1234'
    app.run(debug=True)
