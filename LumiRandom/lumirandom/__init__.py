from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_user import UserManager
import psycopg2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'something only you know'

# Uncomment this block and comment bottom block to switch from PostGreSQL to SQLite
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# db = SQLAlchemy(app)

# Uncomment this block and comment above two lines to switch from SQLite to PostGreSQL
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{username}:{password}@{host}:{port}/{database}'\
#     .format(
#         username='postgres',
#         password='Jczk1241',      # Change accordingly
#         host='localhost',
#         port=5432,
#         database='postgre'   # Change accordingly
#     )

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{username}:{password}@{host}:{port}/{database}'\
    .format(
        username='postgres',
        password='cs2102',      # Change accordingly
        host='localhost',
        port=5432,
        database='lumirandom'   # Change accordingly
    )

app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
db.init_app(app)

# connection = psycopg2.connect(user="postgres", password="Jczk1241", host="localhost", port="5432", database="postgres")
connection = psycopg2.connect(user="postgres", password="cs2102", host="localhost", port="5432", database="lumirandom")

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from lumirandom import routes