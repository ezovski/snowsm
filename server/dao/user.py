import datetime

__author__ = 'mattezovski'

from database import db
from flask.ext.login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode)
    password = db.Column(db.Unicode)
    key = db.Column(db.Text)
    name = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    email = db.Column(db.Text)
