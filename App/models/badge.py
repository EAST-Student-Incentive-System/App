from App.database import db
from .student_badge import StudentBadge

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    points_required = db.Column(db.Integer, nullable=False)

    student_badges = db.relationship('StudentBadge', back_populates='badge', cascade="all, delete-orphan")
    
    def get_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'pointsRequired': self.points_required
        }

    def __repr__(self):
        return f'<Badge {self.name}>'
    
    def meets_requirements(self, student):
        return student.points >= self.points_required
    
    def award_to_student(self, student):
        if self.meets_requirements(student):
            student_badge = StudentBadge(student_id=student.id, badge_id=self.id)
            db.session.add(student_badge)
            db.session.commit()
            return True
        return False
