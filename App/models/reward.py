from App.database import db

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    pointCost = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, default=True)
    students = db.relationship('Student', secondary='redeemed_reward', backref=db.backref('reward', lazy='True'))

    def __init__(self, name, description, pointCost, active=True):
        self.name = name
        self.description = description
        self.pointCost = pointCost
        self.active = active

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
            'active': self.active
        }
    
    def __repr__(self):
        return f'<Reward {self.name}> - {self.pointCost} points'
        
    def isRedeemable(self, user_points):
        return self.active and user_points >= self.pointCost