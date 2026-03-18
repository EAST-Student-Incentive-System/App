from App.database import db
from datetime import datetime, timedelta

class Attendance(db.Model):
    __tablename__ ='attendance'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    student = db.relationship('Student', back_populates='attendances')
    event = db.relationship('Event', back_populates='attendances')


    def get_json(self):
        return {
            'id': self.id,
            'studentId': self.student_id,
            'eventId': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'event': {
                'id': self.event.id,
                'name': self.event.name,
                'type': self.event.type,
                'description': self.event.description,
                'location': self.event.location,
                'start': self.event.start.isoformat(),
                'end': self.event.end.isoformat()
            } if self.event else None
        }

    def __repr__(self):
        return f'<Attendance Student:{self.student_id} Event:{self.event_id}>'
    
    def __init__ ( self, student_id, event_id, timestamp=None):
        self.student_id = student_id
        self.event_id = event_id
        if timestamp:
            self.timestamp = timestamp
        else:
            self.timestamp = datetime.now()
            
    def is_suspicious(self):
        # Check if they are attending multiple events within a short time frame (e.g., 1 hour)
        recent_attendances = Attendance.query.filter(
            Attendance.student_id == self.student_id,
            Attendance.id != self.id,
            Attendance.timestamp >= self.timestamp - timedelta(hours=1)
        ).all()
        return len(recent_attendances) > 0  # Return True if any recent attendances are found

#test
