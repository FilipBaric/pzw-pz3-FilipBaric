from flask import Flask, render_template, session, redirect,url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators, BooleanField, Form
from wtforms.validators import DataRequired, InputRequired
from flask_sqlalchemy import SQLAlchemy
from wtforms.fields.html5 import EmailField
from flask_login import UserMixin
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask import request
import os

apartmani = [
    {"id": 1, "naslov": "Apartman 1", "cijena": 3999},
    {"id": 2, "naslov": "Apartman 2", "cijena": 6999},
    {"id": 3, "naslov": "Apartman 3", "cijena": 8999}
]


app = Flask(__name__)
Bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = "TAJNIKLJUC"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'WebProgDB.sqlite')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#Klasa za login formu
class LoginForm(FlaskForm):
    name = StringField("Username", validators = [DataRequired(), validators.Length(min = 5, max = 25)])
    password = PasswordField("Password", validators= [DataRequired()])
    remember_me = BooleanField('Ostani prijavljen')
    submit = SubmitField("Login")

#Klasa za registracijsku formu
class RegisterForm(FlaskForm):
    name = StringField("Unesite korisničko ime",validators = [DataRequired(), validators.Length(min = 5, max = 25)])
    email = StringField("Unesite vaš email", [validators.DataRequired(), validators.Email(message='Nevaljana email adresa')])
    password = PasswordField("Unesite lozinku", [validators.DataRequired(),
        validators.EqualTo("ponovi", message = "Lozinke moraju biti iste"),validators.Length(min=10, max=25, message='Lozinka mora imati od 10 do 25 znakova')])
    ponovi = PasswordField("Ponovite vašu lozinku")
    prihvati_terms = BooleanField("Prihvaćam uvjete", [validators.DataRequired()])
    register = SubmitField("Registriraj se")

#Klasa za stvaranje usera
class User(UserMixin, db.Model):
    __tablename__ = 'LoginForm'
    id = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(64))
    Password = db.Column(db.String)
    Email = db.Column(db.String)
    def __repr__(self):
        return '<User %r>' % (self.username, self.email)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    return render_template("index.html", name = session.get("name", None))

#Ruta u kojoj ruta ima metode 'POST' i 'GET'. Funkcija sluzi za izradu forme za ulogiranje
@app.route("/login.html", methods = ["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(Username=form.name.data).first()
        if user is not None:
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('index')
            flash('Dobrodošli!', category='success')
            return redirect(url_for("index"))
        flash('Nepoznato korisničko ime ili zaporka', category='warning')
    return render_template("login.html", form = form)

@app.route('/signout.html')
@login_required
def sign_out():
    logout_user()
    return redirect(url_for('index'))

@app.route("/galerija.html")
def galerija():
    return render_template("galerija.html")

@app.route("/pricing.html")
def pricing():
    return render_template("pricing.html", apartmani = apartmani)

@app.route("/checkout.html/<id>")
def checkout(id):
    apartman = [a for a in apartmani if a["id"] == int(id) ][0]
    return render_template("checkout.html", apartman = apartman)

@app.route("/zahvala.html")
def zahvala():
    return render_template("zahvala.html")

@app.route("/kontakti.html")
def kontakti():
    return render_template("kontakti.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"),500

#Ruta za registraciju.
@app.route("/register.html", methods=['GET','POST'])
def registracija():
    form = RegisterForm()
    if form.validate_on_submit():
        last_name = session.get('name')
        user = User.query.filter_by(Username = form.name.data).first()
        if user is None:
            user = User(Username = form.name.data, Email = form.email.data, Password = form.password.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = True
            flash('Uspješno ste se registrirali!')
            return redirect(url_for('index'))
        else:
            session['known'] = False
            flash("Korisnik već postoji")
    return render_template('register.html', form = form, name = session.get('name'), known = session.get('known', False))