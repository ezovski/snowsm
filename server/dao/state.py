__author__ = 'mattezovski'

from database import db

class State(db.Model):

    abbr = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    ski_areas = db.relationship('SkiArea')
