from .user import create_user
from App.database import db


def initialize():
    db.drop_all()
    db.create_all()
    create_user('bob@my.uwi.edu', 'bob', 'bobpass')
    create_user('jane@sta.uwi.edu', 'jane', 'janepass')
    
