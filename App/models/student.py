from App.database import db
from .user import User
from .attendance import Attendance
from .redeemed_reward import RedeemedReward
from .student_badge import StudentBadge


class Student(User):
    __tablename__ = 'student'

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    points = db.Column(db.Integer, default=0, nullable=False)

    attendances = db.relationship('Attendance', back_populates='student', cascade="all, delete-orphan")
    redeemed_rewards = db.relationship('Reward', secondary=RedeemedReward.__table__, backref='redeeming_students')
    badges = db.relationship('Badge', secondary=StudentBadge.__table__, backref='students')

    __mapper_args__ = {
        'polymorphic_identity': 'student',
    }

    def add_points(self, amount):
        self.points += amount

    def subtract_points(self, amount):
        if self.points >= amount:
            self.points -= amount
            return True
        return False

    def get_json(self):
        data = super().get_json()
        data.update({
            'points': self.points,
            'badges': [badge.get_json() for badge in self.badges]
        })
        return data

    def __repr__(self):
        return f'<Student {self.username}> - {self.points} points'

