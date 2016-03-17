import ujson
from database import db
from flask import request, jsonify
from flask.ext.login import login_required
# from web import make_user
from server.services.users_service import make_user

__author__ = 'mattezovski'


def setup_users_routes(app):
    @app.route('/api/userlist', methods=['POST'])
    @login_required
    def create_multiple_users():

        d = ujson.loads(request.get_data())

        if 'names' in d:

            names = d['names'].split(',')
            for n in names:

                if not n:
                    continue
                # Create a new user
                u = make_user(n.strip())
                db.session.add(u)

            db.session.commit()

        resp = jsonify({'success': True})
        return resp