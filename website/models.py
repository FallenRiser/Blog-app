from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_manager,UserMixin
from sqlalchemy import column

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///database.db'
db = SQLAlchemy(app)

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    created_date = db.Column(db.String)
    name = db.Column(db.String)
    email = db.Column(db.String, unique = True)
    password = db.Column(db.String)
    username = db.Column(db.String, unique = True)