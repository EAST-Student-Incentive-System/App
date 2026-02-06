from App.database import db
from .user import User
from .event import Event

class Staff(User):
  __tablename__ = 'staff'
  id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
  events = db.relationship('Event', backref='user',lazy=True)
  __mapper_args__ = {
    'polymorphic_identity': 'staff',
  }

  def get_json(self):
    data = super().get_json()
    data.update({
      'events': [event.get_json() for event in self.events]
    })
    return data
    
  def __repr__(self):
    return f'<Staff {self.username}> - {self.email}'

        
