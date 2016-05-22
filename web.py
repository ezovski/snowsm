import datetime
import os
import os.path
import uuid
from rq_dashboard import RQDashboard

from flask import Flask, render_template, redirect, url_for, jsonify, request, make_response
from flask.ext.login import current_user, login_user, LoginManager, UserMixin, login_required
from flask.ext.restless import APIManager, ProcessingException
from flask.ext.migrate import Migrate, MigrateCommand
from flask_sslify import SSLify
from flask.ext.script import Manager as ScriptManager
from database import db as dbnew
from server.dao.user import User
from server.dao.lift import Lift
from server.dao.skiarea import SkiArea
from server.dao.trail import Trail
from server.dao.state import State

# Step 1: setup the Flask application.
from server.services.users_service import make_user

app = Flask(__name__)
app.config['DEBUG'] = False if os.getenv('IS_HEROKU', False) else True
## Set the following to True to avoid auth issues.
# app.config['TESTING'] = True
app.config['SECRET_KEY'] = '~\x88\xb1\xfa\xb0\xe5\xaf\x82\x18\xc3\xfd\xff\xff\x80=\x9e\x90\x976\xb7\xb3\xbbN\x84'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL','postgres://%s' % 'apiski:@localhost/apiski')
app.config['REDIS_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379')
sslify = SSLify(app, skips=[])
# Old line
#sslify = SSLify(app, skips=['static'])

# Enable rq-dashboard
import queues
rqd = RQDashboard(app=app)

# Step 2: initialize extensions.
dbnew.init_app(app)
db = dbnew
db.app = app
migrate = Migrate(app, db)
api_manager = APIManager(app, flask_sqlalchemy_db=db)
script_manager = ScriptManager(app)
script_manager.add_command('db', MigrateCommand)
login_manager = LoginManager()
login_manager.login_view = '/login'
login_manager.setup_app(app)

# Step 5: this is required for Flask-Login.
@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)


# Step 7: create endpoints for the application, one for index and one for login
@app.route('/', methods=['GET'])
@login_required
def index():
    resp = make_response(render_template('index.html'))
    resp.set_cookie('name', current_user.name if current_user.name else '')

    return resp

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not current_user.is_authenticated():
        u = make_user()
        db.session.add(u)
        db.session.commit()
        login_user(u, remember=True)
        resp = jsonify({'success': True})

    if 'next' in request.args:
        resp = redirect(request.args['next'])

    resp = make_response(resp)
    resp.set_cookie('name', current_user.name if current_user.name else '')

    return resp


@app.route('/login/<user_id>/', methods=['GET'])
def login_as_user(user_id):
    # TODO: Must restrict this path to only work if you have a valid groupsession key.
    login_user(User.query.get(user_id), remember=True)
    resp = jsonify({'success': True})

    resp = make_response(resp)
    resp.set_cookie('name', current_user.name if current_user.name else '')

    return resp

# Step 8: create the API for User with the authentication guard.
def auth_func(**kw):
    if not current_user.is_authenticated():
        raise ProcessingException(description='Not Authorized', code=401)
    if request.method in ['POST']:
        kw['data']['user_id'] = current_user.id

def auth_func_user(**kw):
    if not current_user.is_authenticated():
        raise ProcessingException(description='Not Authorized', code=401)

def init_api():

    api_manager.create_api(Trail, methods=['GET'], exclude_columns=['path', 'ski_area.boundary'], results_per_page=100, collection_name='trails')
    api_manager.create_api(Lift, methods=['GET'], exclude_columns=['path', 'ski_area.boundary'], results_per_page=100, collection_name='lifts')
    api_manager.create_api(SkiArea, methods=['GET'], exclude_columns=['boundary', 'trails.path', 'lifts.path'], results_per_page=100, collection_name='ski_areas')
    api_manager.create_api(State, methods=['GET'], exclude_columns=['ski_areas.boundary'], results_per_page=100, collection_name='states')
    pass

# Step 9: configure and run the application
@script_manager.command
def run():

    init_api()

    app.run()

@script_manager.command
def build_db(geoId):

    import process_trails
    process_trails.build_db(geoId)

@script_manager.command
def update_ski_areas():

    import update_ski_areas
    update_ski_areas.update()

if __name__ == '__main__':

    script_manager.run()

if os.getenv('IS_HEROKU', False):

    init_api()
