import json
from database import db
import requests
from server.dao.skiarea import SkiArea
import us

__author__ = 'mattezovski'

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

                sa.state_abbr = us.states.lookup(resp['address']['state']).abbr

    db.session.commit()
