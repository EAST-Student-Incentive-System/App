from App.database import db

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    pointCost = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, default=True)

    def __init__(self, name, description, pointCost, active=True):
        self.name = name
        self.description = description
        self.pointCost = pointCost
        self.active = active