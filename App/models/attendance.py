from App.database import db
from datetime import datetime, timedelta

class Attendance(db.Model):
    __tablename__ ='attendance'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    device_info = db.Column(db.String(255), nullable=True)  # Optional field to store device information for additional fraud detection

    student = db.relationship('Student', back_populates='attendances')
    event = db.relationship('Event', back_populates='attendances')


    def get_json(self):
        return {
            'id': self.id,
            'studentId': self.student_id,
            'eventId': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'overlaps': [
            {
                'eventId': att.event.id,
                'eventName': att.event.name,
                'timestamp': att.timestamp.isoformat()
            }
            for att in self.get_overlap_events()
        ],
            'event': {
                'id': self.event.id,
                'name': self.event.name,
                'type': self.event.type,
                'description': self.event.description,
                'location': self.event.location,
                'start': self.event.start.isoformat(),
                'end': self.event.end.isoformat()
            } if self.event else None,
        
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

    
    def get_overlap_events(self):
        all_attendances = Attendance.query.filter(
            Attendance.student_id == self.student_id,
            Attendance.id != self.id
        ).all()

        overlaps = []
        print("CHECKING FOR OVERLAP EVENTS FOR ATTENDANCE:", self)

        for att in all_attendances:
                    if att.timestamp.date() == self.timestamp.date():
        # Then check if within ±1 hour
                        if self.timestamp - timedelta(hours=1) <= att.timestamp <= self.timestamp + timedelta(hours=1):
                            print(f"Found overlapping attendance: {att} for event {att.event.name} at {att.timestamp}")
                            overlaps.append(att)

        return overlaps

    def get_device_conflicts(self):
        if not self.device_info:
            return []
        return Attendance.query.filter(
            Attendance.device_info == self.device_info,
            Attendance.student_id != self.student_id,
            Attendance.event_id == self.event_id
        ).all()


