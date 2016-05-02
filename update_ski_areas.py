import json
from database import db
import requests
from server.dao.skiarea import SkiArea
import us
from unidecode import unidecode

__author__ = 'mattezovski'

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
    'YT': 'Yukon',
    'Alberta': 'AB',
    'British Columbia': 'BC',
    'Manitoba': 'MB',
    'New Brunswick': 'NB',
    'Newfoundland and Labrador': 'NL',
    'Northwest Territories': 'NT',
    'Nova Scotia': 'NS',
    'Nunavut': 'NU',
    'Ontario': 'ON',
    'Prince Edward Island': 'PE',
    'Quebec': 'QC',
    'Saskatchewan': 'SK',
    'Yukon': 'YT'
}

def update():

    sa_list = SkiArea.query.all()

    for sa in sa_list:

        # Add updates to be processed here

        if not sa.state_abbr:

            url = 'http://nominatim.openstreetmap.org/reverse?format=json&osm_id=' + str(sa.osm_id)

            # Ping nominatim for info about node
            if sa.inferred:

                # OSM object is a node
                url += '&osm_type=N'

            else:

                # OSM object is a way
                url += '&osm_type=W'

            resp = requests.get(url)

            resp = json.loads(resp.text)
            if 'address' in resp and 'state' in resp['address']:

                #sa.state_abbr = us.states.lookup(resp['address']['state']).abbr
                state = us.states.lookup(resp['address']['state'])
                if state:
                    sa.state_abbr = state.abbr
                else:
                    # Assume Canada for now
                    if unidecode(resp['address']['state']) in prov_terr:
                        sa.state_abbr = prov_terr[unidecode(resp['address']['state'])]

    db.session.commit()
