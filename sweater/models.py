from flask_login import UserMixin
from flask_socketio import send
import enum
from sqlalchemy import Enum
from sweater import db, manager
from datetime import datetime, timezone

class User (db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    login = db.Column(db.String(50), nullable = False, unique = True)
    email = db.Column(db.String(255), nullable = False)
    password = db.Column(db.String(255), nullable = False)
    media_path = db.Column(db.String(200))

@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class News (db.Model):
    id = db.Column(db.Integer, primary_key = True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(50), nullable = False)
    text = db.Column(db.String(255), nullable = False)
    media_path = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable = False )
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now(timezone.utc))
    author = db.relationship('User', backref='news')
    comments = db.relationship('Comment', backref='news', lazy=True)

class Comment (db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Связь с пользователем 


class Gender(enum.Enum):
    male = "male"
    female = "female"

class User_info (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    birthday = db.Column(db.DateTime)
    sex = db.Column(Enum(Gender), nullable=False)  # Поле sex, которое может принимать одно из значений перечисления
    hobby = db.Column(db.String(100))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    text = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))

