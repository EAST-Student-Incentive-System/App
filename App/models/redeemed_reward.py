from App.database import db
from datetime import datetime

class RedeemedReward(db.Model):
    __tablename__ ='redeemed_reward'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    reward_id = db.Column(db.Integer, db.ForeignKey('reward.id'), nullable=False)
    redeemed_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    reward = db.relationship('Reward', back_populates='redeemed_rewards', overlaps="students,redeemed_rewards")
    isValid = db.Column(db.Boolean, default=True)

    def get_json(self):
        return {
            'id': self.id,
            'studentId': self.student_id,
            'rewardId': self.reward_id,
            'rewardName': self.reward.name if self.reward else None,
            'rewardDescription': self.reward.description if self.reward else None,
            'pointCost': self.reward.pointCost if self.reward else None,
            'redeemedAt': self.redeemed_at.isoformat(),
            'isValid': self.isValid
        }

    def __repr__(self):
        return f'<RedeemedReward Student:{self.student_id} Reward:{self.reward_id}>'
    
    def __init__ (self, student_id, reward_id, redeemed_at=None):
        self.student_id = student_id
        self.reward_id = reward_id
        if redeemed_at:
            self.redeemed_at = redeemed_at
        else:
            self.redeemed_at = datetime.now()
