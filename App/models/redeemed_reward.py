from App.database import db
from datetime import datetime

class RedeemedReward(db.Model):
    __tablename__ ='redeemed_reward'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    reward_id = db.Column(db.Integer, db.ForeignKey('reward.id'), nullable=False)
    redeemed_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def get_json(self):
        return {
            'id': self.id,
            'studentId': self.student_id,
            'reward': self.reward.get_json(),
            'redeemedAt': self.redeemed_at.isoformat()
        }

    def __repr__(self):
        return f'<RedeemedReward Student:{self.student_id} Reward:{self.reward_id}>'
