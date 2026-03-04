from App.database import db
from datetime import datetime
from .attendance import Attendance
from .student import Student
from App.models.student_event import student_event
from flask import url_for

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staffId = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False) #Update to enum later when types are finalized
    description = db.Column(db.String(300), nullable=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=True)
    attendances = db.relationship('Attendance', back_populates='event', cascade="all, delete-orphan")
    students = db.relationship('Student', secondary=student_event, back_populates='events')
    qr = db.Column(db.Text, nullable=True) #store QR code data or path here, can be generated on demand or stored after creation
    image = db.Column(db.String(200), nullable=True) #optional image for event, can be used in UI to make it more appealing

    @property
    def image_url(self):
        if self.image:
            return url_for('static', filename=f'uploads/{self.image}')
        return None

    def get_json(self):
        return {
            'id': self.id,
            'staffId': self.staffId,
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'start': self.start.isoformat(),
            'end': self.end.isoformat(),
            'location': self.location,
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

    
