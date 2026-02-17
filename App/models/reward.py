from App.database import db
from .redeemed_reward import RedeemedReward


class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    pointCost = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, default=True)
    students = db.relationship('Student', secondary=RedeemedReward.__table__, back_populates='redeemed_rewards')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    creator = db.relationship('User', backref=db.backref('created_rewards', lazy=True))

    def __init__(self, name, description, pointCost, active=True, created_by=None):
        self.name = name
        self.description = description
        self.pointCost = pointCost
        self.active = active
        self.created_by = created_by

    def toggle(self):
        self.active = not self.active
        db.session.add(self)
        db.session.commit()

    def get_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'pointCost': self.pointCost,
            'active': self.active,
            'createdBy': self.created_by
        }

    def __repr__(self):
        return f'<Reward {self.name}> - {self.pointCost} points'

    def isRedeemable(self, user_points):
        return self.active and user_points >= self.pointCost