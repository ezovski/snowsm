__author__ = 'mattezovski'

from database import db
from geoalchemy2 import Geometry


class Trail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    osm_id = db.Column(db.BigInteger, unique=True)
    ski_area = db.relationship('SkiArea', back_populates='trails')
    ski_area_id = db.Column(db.Integer, db.ForeignKey('ski_area.id'))
    difficulty = db.Column(db.Text)
    path = db.Column(Geometry())