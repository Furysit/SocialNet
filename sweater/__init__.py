from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SECRET_KEY'] = 'fury'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:123@localhost/social'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
migrate = Migrate(app,db)
manager = LoginManager(app)
socketio = SocketIO(app, cors_allowed_origins = '*')

from sweater import routes,models