from .user import create_user
from .badge import createBadge
from App.database import db


def initialize():
    db.drop_all()
    db.create_all()
    create_user('bob@my.uwi.edu', 'bob', 'bobpass')
    create_user('jane@sta.uwi.edu', 'jane', 'janepass')
    createBadge('25 Points', 'Awarded for earning 50 points', 25)
    createBadge('50 Points', 'Awarded for earning 50 points', 50)
    createBadge('75 Points', 'Awarded for earning 50 points', 75)
    
