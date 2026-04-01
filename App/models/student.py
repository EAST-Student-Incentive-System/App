import uuid
from App.database import db
from .user import User
from .redeemed_reward import RedeemedReward
from .student_badge import StudentBadge
from App.models.reward import Reward
from App.models.student_event import student_event
from sqlalchemy.orm import relationship, Mapped, mapped_column
from App.models.attendance import Attendance

class Student(User):
    __tablename__ = 'student'

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    total_points = db.Column(db.Integer, default=0, nullable=False)
    redeemed_points = db.Column(db.Integer, default=0, nullable=False)
    current_balance = db.Column(db.Integer, default=0, nullable=False)
    avatar_seed = db.Column(db.String(100), nullable=False, default=lambda: str(uuid.uuid4()))

    attendances = db.relationship('Attendance', back_populates='student', cascade="all, delete-orphan")
    redeemed_rewards = db.relationship('Reward', secondary=RedeemedReward.__table__, back_populates='students', overlaps="reward,students")
    student_badges = db.relationship('StudentBadge', back_populates='student', cascade="all, delete-orphan")
    events = db.relationship("Event", secondary=student_event, back_populates="students")
    appeal_desc = db.Column(db.Text, nullable=True)
    appeal_image = db.Column(db.String(256), nullable=True)
    appeal_status = db.Column(db.String(20), nullable=True)  # "pending" | "approved" | "rejected"
    timeout_count = db.Column(db.Integer, default=0)
    temporary_gps_holder = db.Column(db.String(64), nullable = True)   # store last GPS attempt
    temporary_device_holder = db.Column(db.String(256), nullable = True)  # store last device attempt
    isFlagged = db.Column(db.Boolean, default=False)
    timeout_until = db.Column(db.DateTime, nullable=True)

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
            'badges': [badge.get_json() for badge in self.student_badges]
        })
        return data

    def __repr__(self):
        return f'<Student {self.username}> - {self.current_balance} points'
    
    def check_enough_points(self, reward) -> bool:
        return self.current_balance >= reward.pointCost

    def get_avatar_url(self, style="fun-emoji"):
        return f"https://api.dicebear.com/9.x/{style}/svg?seed={self.avatar_seed}"

    def regenerate_avatar(self):
        self.avatar_seed = str(uuid.uuid4())
    

    

