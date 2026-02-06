from App.database import db
from datetime import datetime

class Attendance(db.Model):
    __tablename__ ='attendance'
    
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    student = db.relationship("Student", back_populates="attendances")
    event = db.relationship("Event", back_populates="attendances")

    def get_json(self):
        return {
            'id': self.id,
            'studentId': self.student_id,
            'eventId': self.event_id,
            'timestamp': self.timestamp.isoformat()
        }

    def __repr__(self):
        return f'<Attendance Student:{self.student_id} Event:{self.event_id}>'
#test
