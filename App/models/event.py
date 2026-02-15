from App.database import db
from datetime import datetime
from .attendance import Attendance
from .student import Student
from App.models.student_event import student_event

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staffId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False) #Update to enum later when types are finalized
    description = db.Column(db.String(300), nullable=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    attendances = db.relationship('Attendance', back_populates='event', cascade="all, delete-orphan")
    students = db.relationship('Student', secondary=student_event, back_populates='events')
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

    def isWithintTimeFrame(self):
        return self.start <= datetime.now() <= self.end
    
    def calculate_point_value(self):
        #points based on duration, 1 point per hour, rounded up, may add modifiers later based on event type or other factors
        duration = self.end - self.start
        hours = duration.total_seconds() / 3600
        return max(1, int(hours + 0.5)) #round up to nearest hour, minimum 1 point

    
