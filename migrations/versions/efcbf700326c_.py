"""empty message

Revision ID: efcbf700326c
Revises: fcbd433f6cf2
Create Date: 2016-05-01 22:18:46.820202

"""

# revision identifiers, used by Alembic.
from database import db
from server.dao.state import State

revision = 'efcbf700326c'
down_revision = 'fcbd433f6cf2'

from alembic import op
import sqlalchemy as sa


def upgrade():

    prov_terr = {
    'AB': 'Alberta',
    'BC': 'British Columbia',
    'MB': 'Manitoba',
    'NB': 'New Brunswick',
    'NL': 'Newfoundland and Labrador',
    'NT': 'Northwest Territories',
    'NS': 'Nova Scotia',
    'NU': 'Nunavut',
    'ON': 'Ontario',
    'PE': 'Prince Edward Island',
    'QC': 'Quebec',
    'SK': 'Saskatchewan',
    'YT': 'Yukon'
    }

    provinces = [{'abbr': abbr, 'name': prov_terr[abbr]} for abbr in prov_terr]
    for x in provinces:
        s = State()
        s.abbr = x['abbr']
        s.name = x['name']
        db.session.add(s)

    db.session.commit()


def downgrade():
    pass

    ### end Alembic commands ###
