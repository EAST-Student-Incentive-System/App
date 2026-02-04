from App.models import Reward, Student
from App.database import db

def view_rewards(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        return []
    rewards = db.session.scalars(db.select(Reward)).all()
    return [r.get_json() for r in rewards if r.isRedeemable(student.points)]

def redeem_reward(student_id, reward_id):
    student = db.session.get(Student, student_id)
    reward = db.session.get(Reward, reward_id)
    if not student or not reward or not reward.isRedeemable(student.points):
        return None
    from App.models import RedeemedReward
    rr = RedeemedReward(student_id=student.id, reward_id=reward.id)
    student.subtract_points(reward.pointCost)
    db.session.add(rr)
    db.session.commit()
    return rr

def get_reward_history(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        return []
    from App.models import RedeemedReward
    return student.redeemed_rewards