from App.database import db
from .user import User

class Staff(User):
    __tablename__ = 'staff'
    events = db.relationship('Event', backref='user',lazy=True)
    __mapper_args__ = {
      'polymorphic_identity': 'staff',
    }
