import uuid
from server.dao.user import User

__author__ = 'mattezovski'


def make_user(name=None, email=None):
    u = User()
    u.key = '{}'.format(uuid.uuid4())
    if name:
        u.name = name
    if email:
        u.email = email
    return u
