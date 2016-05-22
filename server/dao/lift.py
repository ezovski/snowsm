import json
import geoalchemy2
from sqlalchemy.ext.hybrid import hybrid_property

__author__ = 'mattezovski'

from database import db
from geoalchemy2 import Geometry


class Lift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    osm_id = db.Column(db.BigInteger, unique=True)
    ski_area = db.relationship('SkiArea')
    ski_area_id = db.Column(db.Integer, db.ForeignKey('ski_area.id'))
    type = db.Column(db.Text)
    path = db.Column(Geometry())
    occupancy = db.Column(db.Integer)

    @hybrid_property
    def geojson(self):

        return json.loads(db.session.scalar(geoalchemy2.functions.ST_AsGeoJSON(self.path)))