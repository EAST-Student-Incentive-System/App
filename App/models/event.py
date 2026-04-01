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
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=True)
    attendances = db.relationship('Attendance', back_populates='event', cascade="all, delete-orphan")
    students = db.relationship('Student', secondary=student_event, back_populates='events')
    image = db.Column(db.String(200), nullable=True) #optional image for event, can be used in UI to make it more appealing
    active = db.Column(db.Boolean, default=False) #soft delete flag, set to False instead of deleting record
    latitude = db.Column(db.Float, nullable=True) #optional latitude for event location
    longitude = db.Column(db.Float, nullable=True) #optional longitude for event location
    radius = db.Column(db.Float, nullable=True) #optional radius in meters for geofencing attendance   
    limit = db.Column(db.Integer, nullable=True) #optional limit on number of attendees, can be used for capacity management or motivation to use app for exclusive events  

    def __init__(self, staffId, name, type, description, start, end, location=None, image=None, active=False, limit=None):
        self.staffId = staffId
        self.name = name
        self.type = type
        self.description = description
        self.start = start
        self.end = end
        self.location = location
       # self.qr = qr
        self.image = image
        self.active = active
        self.limit = limit

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
            'image' : self.image,
            #'qr': self.qr,
            'active': self.active
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

    
