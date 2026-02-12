from App.database import db
from .user import User
from .attendance import Attendance
from .redeemed_reward import RedeemedReward
from .student_badge import StudentBadge
from App.models.reward import Reward


class Student(User):
    __tablename__ = 'student'

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    total_points = db.Column(db.Integer, default=0, nullable=False)
    redeemed_points = db.Column(db.Integer, default=0, nullable=False)
    current_balance = db.Column(db.Integer, default=0, nullable=False)

    attendances = db.relationship('Attendance', back_populates='student', cascade="all, delete-orphan")
    redeemed_rewards = db.relationship('Reward', secondary=RedeemedReward.__table__, backref='redeeming_students')
    badges = db.relationship('Badge', secondary=StudentBadge.__table__, backref='students')
    events = db.relationship('Event', secondary='attendance', back_populates='students')

    __mapper_args__ = {
        'polymorphic_identity': 'student',
    }

    def add_points(self, amount):
        if amount <= 0:
            return
        self.total_points += int(amount)
        self.current_balance += int(amount)

    def subtract_points(self, amount):
        if amount <= 0:
            return False
        if self.current_balance >= amount:
            amt = int(amount)
            self.redeemed_points += amt
            self.current_balance -= amt
            return True
        return False

    def get_json(self):
        data = super().get_json()
        data.update({
            'total_points': self.total_points,
            'redeemed_points': self.redeemed_points,
            'current_balance': self.current_balance,
            'badges': [badge.get_json() for badge in self.badges]
        })
        return data

    def __repr__(self):
        return f'<Student {self.username}> - {self.current_balance} points'
    
    def check_enough_points(self, reward):
        return self.current_balance >= reward.pointCost
    

    

