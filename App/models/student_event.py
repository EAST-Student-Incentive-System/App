from App.database import db
from datetime import datetime


student_event = db.Table(
    'student_event',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)

def __init__(self, student_id, event_id):
    self.student_id = student_id
    self.event_id = event_id,
    self.joined_at = datetime.now()
