from App.models import Reward, Student, RedeemedReward
from App.database import db


def view_redeemed_rewards(student_id):
    student = Student.query.get(student_id)
    if not student:
        return None
    # Return ORM objects directly
    return RedeemedReward.query.filter_by(student_id=student_id).all()
