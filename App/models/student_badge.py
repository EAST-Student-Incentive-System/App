from App.database import db
from datetime import datetime

class StudentBadge(db.Model):
    __tablename__ ='student_badge'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badge.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    student = db.relationship('Student', back_populates='student_badges')
    badge = db.relationship('Badge', back_populates='student_badges')

    def get_json(self):
        return {
            'id': self.id,
            'badge': self.badge.get_json(),
            'earnedAt': self.earned_at.isoformat()
        }

    def __repr__(self):
        return f'<StudentBadge Student:{self.student.id} Badge:{self.badge_id}>'
