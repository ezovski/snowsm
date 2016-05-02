from server.dao.lift import Lift
from database import db
import update_ski_areas
__author__ = 'mattezovski'

from shapely import geometry

import overpass

from server.dao.trail import Trail
from server.dao.skiarea import SkiArea

PACIFIC_BB = '26.6670958011,-169.27734375,71.6636629314,-114.78515625'
ROCKIES_BB = '26.6670958011,-114.9609375,71.6636629314,-98.26171875'
CENTRAL_BB = '26.6670958011,-98.4375,71.6636629314,-74.53125'
EAST_BB = '26.6670958011,-74.53125,71.6636629314,-50.9765625'

BB_LIST = [
    PACIFIC_BB,
    ROCKIES_BB,
    CENTRAL_BB,
    EAST_BB
]

def build_query(query, bb):

    return query + bb + ');'

def build_db(geoId):
    api = overpass.API(timeout=10000)

    # New Hampshire and some surrounding areas
    BOUNDING_BOX = '43.12103377575541,-73.7237548828125,44.797428998555674,-69.378662109375'

    if geoId:
        BOUNDING_BOX = BB_LIST[int(geoId)]

    # Core of White Mountains
    #BOUNDING_BOX = '44.00269350325321,-71.64871215820312,44.36067856998804,-71.12411499023438'

    # All of NE US/CAN
    #BOUNDING_BOX = '37.70120736474139,-81.7822265625,49.23912083246698,-64.40185546874999'

    # response = api.Get('node["name"="Salt Lake City"]')
    # response = api.Get('way["piste:type"~"downhill|yes"](44.00269350325321,-71.64871215820312,44.36067856998804,-71.12411499023438)')
    print('getting trails')
    trail_response = api.Get(build_query('way["piste:type"~"downhill|yes"](', BOUNDING_BOX), 'json')

    print('getting lifts')
    lift_response = api.Get(build_query('way["aerialway"~""](',BOUNDING_BOX), 'json')

    print('getting ski areas')
    ski_area_response = api.Get(build_query('way["landuse"~"winter_sports"](', BOUNDING_BOX), 'json')

    ski_areas = []
    trails = []
    lifts = []
    print('storing ski areas')
    for sa in ski_area_response.features:

        exists = SkiArea.query.filter_by(osm_id=sa['id'])
        if exists.count():
            #TODO: Allow ski area updates to process
            continue

        sam = SkiArea()
        sam.name = sa['properties'].get('name')
        if not sam.name:
            continue
        sam.osm_id = sa['id']
        sam.boundary = str(geometry.Polygon(sa['geometry']['coordinates']))
        ski_areas.append(sam)
        db.session.add(sam)

    db.session.commit()

    print('storing trails')
    for trail in trail_response.features:

        if trail['properties'].get('name') is None:
            continue
        exists = Trail.query.filter_by(osm_id=trail['id'])
        if exists.count():
            t = exists[0]
        else:
            t= Trail()

        t.name = trail['properties'].get('name')
        t.difficulty = trail['properties'].get('piste:difficulty').lower() if 'piste:difficulty' in trail['properties'] else None
        t.osm_id = trail['id']
        t.path = str(geometry.LineString(trail['geometry']['coordinates']))

        if not exists.count():
            db.session.add(t)
        db.session.commit()

        if not exists.count():
            # Remaining steps only apply to new trails
            continue

        # Determine which ski area this trail is a part of.
        # results = db.session.query(SkiArea).filter(SkiArea.boundary.ST_Contains(geoalchemy2.WKBElement(geometry.LineString(trail['geometry']['coordinates']))))
        results = db.session.query(SkiArea).filter(SkiArea.boundary.ST_Intersects(t.path))
        if results.count() > 1:
            print('way ' + str(trail['id']) + ' is confused')

        if results.count() > 0:
            t.ski_area_id = results[0].id
            continue

        # if results.count() != 1:
        results = find_nearest_ski_area(t)

        if results:
            t.ski_area_id = results
            continue

        # Attempt to locate and create a different kind of ski area.
        lat_lon = str(trail.geometry.coordinates[0][1]) + ',' + str(trail.geometry.coordinates[0][0])
        sc_query = 'node(around:1700,' + lat_lon + ')[leisure=sports_centre];'
        sports_centre_response = api.Get(sc_query, 'json')
        if len(sports_centre_response.features) > 0:
            if len(sports_centre_response.features) > 1:
                print('way ' + str(trail['id']) + ' is confused')
            sa = sports_centre_response.features[0]
            sam = SkiArea()
            sam.inferred = True
            sam.name = sa['properties'].get('name')
            if not sam.name:
                continue
            sam.osm_id = sa['id']
            sam.boundary = str(geometry.Point(sa['geometry']['coordinates']).buffer(0.020))
            #sam.boundary = str(geometry.Point(sa['geometry']['coordinates']))
            db.session.add(sam)
            t.ski_area = sam
            # t.ski_area = sam
            db.session.commit()

    db.session.commit()

    print('storing lifts')
    for lift in lift_response.features:

        exists = Lift.query.filter_by(osm_id=lift['id'])
        if exists.count():
            #TODO: Allow lift updates to process
            continue

        lt = Lift()
        lt.name = lift['properties'].get('name')
        lt.type = lift['properties'].get('aerialway')
        lt.osm_id = lift['id']
        lt.path = str(geometry.LineString(lift['geometry']['coordinates']))

        db.session.add(lt)
        db.session.commit()

        results = db.session.query(SkiArea).filter(SkiArea.boundary.ST_Contains(lt.path))
        if results.count() == 1:

            lt.ski_area_id = results[0].id
            continue

        results = find_nearest_ski_area(lt)
        if results:
            lt.ski_area_id = results

    db.session.commit()

    # Clean up results.

    # Cycle through unaffiliated lifts. Attempt to affiliate.
    # Continue to cycle until all lifts have affiliated or iterating isn't helping.
    lifts = Lift.query.filter_by(ski_area_id = None)
    num_unaffiliated_lifts = lifts.count()

    while num_unaffiliated_lifts > 0:
        print(num_unaffiliated_lifts)

        for lt in lifts:

            result = find_nearest_ski_area(lt)
            if result:
                lt.ski_area_id = result
                db.session.commit()

        lifts = Lift.query.filter_by(ski_area_id = None)
        if lifts.count() == num_unaffiliated_lifts:
            break

        num_unaffiliated_lifts = lifts.count()

    # Cycle through unaffiliated trails. Attempt to affiliate.
    # Continue to cycle until all trails have affiliated or iterating isn't helping.

    trails = Trail.query.filter_by(ski_area_id = None)
    num_unaffiliated_trails = trails.count()

    while num_unaffiliated_trails > 0:

        print(num_unaffiliated_trails)

        for t in trails:

            result = find_nearest_ski_area(t)
            if result:
                t.ski_area_id = result
                db.session.commit()

        trails = Trail.query.filter_by(ski_area_id = None)
        if trails.count() == num_unaffiliated_trails:
            break

        num_unaffiliated_trails = trails.count()

    # Associates ski areas with states
    # TODO: Rename all of this.
    update_ski_areas.update()

    print 'done'


def find_nearest_ski_area(entity):

    results = db.session.query(Trail).filter(Trail.ski_area_id != None, Trail.path.ST_Distance(entity.path) < .005)

    if results.count() > 0:
        return results[0].ski_area_id

    results = db.session.query(Lift).filter(Lift.ski_area_id != None, Lift.path.ST_Distance(entity.path) < .005)

    if results.count() > 0:

        return results[0].ski_area_id

    results = db.session.query(SkiArea).filter(SkiArea.inferred == False, SkiArea.boundary.ST_Distance(entity.path) < .025)

    if results.count() > 0:

        return results[0].id

    return None