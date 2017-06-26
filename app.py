from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import articles
from wtforms.fields.html5 import EmailField
from flask_mysqldb import MySQL
from wtforms import StringField, TextAreaField, PasswordField, validators
from flask_wtf import FlaskForm
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.secret_key = 'llavesecreta123'
# Se debe llamar la funcion aqui, y se guarda en una variable
Articles = articles()


@app.route('/')
def hello_world():
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


class MyForm(FlaskForm):
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
        return render_template('register.html')

    return render_template('register.html', form=form)
if __name__ == '__main__':
    app.run(debug=True)
