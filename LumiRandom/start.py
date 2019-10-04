from flask import Flask, redirect, render_template, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, LoginManager, UserMixin, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, Form, TextField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from sqlalchemy.orm import sessionmaker

isstudent = False
istutor = False

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{username}:{password}@{host}:{port}/{database}'\
    .format(
        username='<username>',
        password='<password>',
        host='localhost',
        port=5432,
        database='<database>'
    )

app.secret_key = "something only you know"
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
database = SQLAlchemy(app)

database.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, database.Model):
    __tablename__ = "users"

    username = database.Column(database.String(128), primary_key = True, nullable = False)
    password = database.Column(database.String(128), nullable = False)
    role = database.Column(database.String(128), nullable = False)
    name = database.Column(database.String(128), nullable = False)
    def get_password(self, password):
        return self.password

    def get_id(self):
        return self.username

@login_manager.user_loader
def load_username(username):
    return User.query.filter_by(username=username).first()

def load_password(password):
    return User.query.filter_by(password = password).first()


@app.route("/")
def home():
    return render_template('index.html')

# @app.route("/register/", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         return (render_template("register.html"))
#     if request.method == "GET":
#         return render_template("register.html")
@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error=False)

    # user = str(request.form['username'])
    # psasword = str(request.form['password'])
    user = load_username(request.form["username"])
    password = load_password(request.form["password"])

    if user is None:
        return render_template("login.html", error = True)
    else:
        if password is None:
            return render_template("login.html", error = True)
        else:
            login_user(user)
    login_user(user)
    print('logged in')
    return redirect(url_for('home'))

@app.route("/register/", methods=["GET", "POST", "PUT"])
def register():
    if request.method == "GET":
        return render_template("register.html", error=False)

    user = (request.form["username"])
    password = (request.form["password"])
    name = (request.form["name"])
    role = (request.form["role"])
    user_check = User.query.filter_by(username=user).first()
    name_check = User.query.filter_by(name = name).first()
    role_check = str(role).lower()
    if user_check is None and name_check is None and (role_check == 'student' or role_check == 'tutor'):
        register = User(name = name, username = user, password = password, role = role)
        database.session.add(register)
        database.session.commit()
        return redirect(url_for('login'))
    else:
        if user_check is not None:
            return render_template("register.html", error1 = True)
        if name_check is not None:
            return render_template("register.html", error2 = True)
        if role_check != 'student' or role_check != 'tutor':
            return render_template("register.html", error3 = True)
    return render_template("register.html")

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    print('logout')
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug = True, host = 'localhost', port = 4000)
