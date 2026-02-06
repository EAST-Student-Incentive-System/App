from App.database import db
from .student_badge import StudentBadge

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    points_required = db.Column(db.Integer, nullable=False)

    student_badges = db.relationship('Student', secondary= StudentBadge.__table__, backref=db.backref('badge', lazy=True))
    
    def get_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'pointsRequired': self.points_required
        }

    def __repr__(self):
        return f'<Badge {self.name}>'
