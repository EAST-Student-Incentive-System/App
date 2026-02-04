from App.database import db
from .user import User

class Student(User):
    __tablename__ = 'student'

    
    points = db.Column(db.Integer, default=0, nullable=False)

    attendances = db.relationship('Event', secondary='attendance', backref=db.backref('student', lazy=True))
    redeemed_rewards = db.relationship('Reward', secondary='redeemed_reward', backref=db.backref('student', lazy=True))
    badges = db.relationship('Badge', secondary='student_badge', backref=db.backref('student', lazy=True))
    
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
    
    def get_points(self):
        return self.points
    
    def check_enough_points(self, amount):
        return self.points >= amount
    
    def add_points(self, amount):
        self.points += amount

    def subtract_points(self, amount):
        if self.points >= amount:
            self.points -= amount
            return True
        return False
    
    def get_badges(self):
        return self.badges
    

