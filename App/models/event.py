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

    def get_json(self):
        return {
            'id': self.id,
            'staffId': self.staffId,
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'start': self.start.isoformat(),
            'end': self.end.isoformat()
        }
    
    def __repr__(self):
        return f'<Event {self.name}> - {self.type} from {self.start} to {self.end}'
    
    def get_staff_id(self):
        return self.staffId
    
    def get_name(self):
        return self.name
    
    def get_type(self):
        return self.type

    def get_description(self):
        return self.description
    
    def get_start(self):
        return self.start
    
    def get_end(self):
        return self.end
    
    def set_name(self, name):
        self.name = name
        db.session.add(self)
        db.session.commit()

    def set_type(self, type):
        self.type = type
        db.session.add(self)
        db.session.commit()

    def set_description(self, description):
        self.description = description
        db.session.add(self)
        db.session.commit()

    def set_start(self, start):
        self.start = start
        db.session.add(self)
        db.session.commit()

    def set_end(self, end): 
        self.end = end
        db.session.add(self)
        db.session.commit()

    def isWithintTimeFrame(self):
        return self.start <= datetime.now() <= self.end
    
