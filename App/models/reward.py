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
    
    def get_name(self):
        return self.name
    
    def get_description(self):
        return self.description
    
    def get_point_cost(self):
        return self.pointCost
    
    def get_active(self):
        return self.active  
    
    def set_name(self, name):
        self.name = name
        db.session.add(self)
        db.session.commit()

    def set_description(self, description):
        self.description = description
        db.session.add(self)
        db.session.commit()

    def set_point_cost(self, pointCost):
        self.pointCost = pointCost
        db.session.add(self)
        db.session.commit()
        
    def isRedeemable(self, user_points):
        return self.active and user_points >= self.pointCost