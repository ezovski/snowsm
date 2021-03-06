import json
import geoalchemy2
from sqlalchemy.ext.hybrid import hybrid_property

__author__ = 'mattezovski'

from database import db
from geoalchemy2 import Geometry


class SkiArea(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    osm_id = db.Column(db.BigInteger, unique=True)
    boundary = db.Column(Geometry())
    inferred = db.Column(db.Boolean, default=False)
    state_abbr = db.Column(db.Text, db.ForeignKey('state.abbr'))
    state = db.relationship('State', back_populates='ski_areas')
    trails = db.relationship('Trail')
    lifts = db.relationship('Lift')

    ### NOT CURRENTLY USED
    # @hybrid_property
    # def boundary_serialized(self):
    #
    #     return json.loads(db.session.scalar(geoalchemy2.functions.ST_AsGeoJSON(self.boundary)))