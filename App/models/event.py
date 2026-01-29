from App.database import db
from datetime import datetime

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staffId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False) #Update to enum later when types are finalized
    description = db.Column(db.String(300), nullable=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)

    def __init__(self, name, type, description, start, end):
        self.name = name
        self.type = type
        self.description = description
        self.start = start
        self.end = end
