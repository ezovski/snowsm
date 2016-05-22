__author__ = 'mattezovski'

from database import db
from geoalchemy2 import Geometry
import geoalchemy2
from sqlalchemy.ext.hybrid import hybrid_property
import json

class Trail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    osm_id = db.Column(db.BigInteger, unique=True)
    ski_area = db.relationship('SkiArea', back_populates='trails')
    ski_area_id = db.Column(db.Integer, db.ForeignKey('ski_area.id'))
    difficulty = db.Column(db.Text)
    path = db.Column(Geometry())

    @hybrid_property
    def geojson(self):

        return json.loads(db.session.scalar(geoalchemy2.functions.ST_AsGeoJSON(self.path)))