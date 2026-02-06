from App.models import Reward, Student
from App.database import db

def redeem_reward(student_id, reward_id):
    student = Student.query.get(student_id)
    reward = Reward.query.get(reward_id)

    if not student or not reward:
        return None

    if student.balance < reward.pointsCost:
        return None

    student.balance = subtract_points(student.balance, reward.pointsCost)
    student.redeemed_rewards.append(reward)
    db.session.commit()

    return reward

def view_redeemed_rewards(student_id):
    student = Student.query.get(student_id)

    if not student:
        return None
    return student.redeemed_rewards