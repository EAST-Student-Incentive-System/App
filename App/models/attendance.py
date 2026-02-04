from App.database import db
from datetime import datetime

class Attendance(db.Model):
    __tablename__ ='attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def get_json(self):
        return {
            'id': self.id,
            'studentId': self.student_id,
            'eventId': self.event_id,
            'timestamp': self.timestamp.isoformat()
        }

    def __repr__(self):
        return f'<Attendance Student:{self.student_id} Event:{self.event_id}>'

    def get_student_id(self):
        return self.student_id
    
    def get_event_id(self):
        return self.event_id
    
    def get_timestamp(self):
        return self.timestamp

    def isfor_event(self, event_id):
        return self.event_id == event_id

