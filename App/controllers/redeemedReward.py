from App.models import Reward, Student
from App.database import db


def view_redeemed_rewards(student_id):
    student = Student.query.get(student_id)

    if not student:
        return None
    return student.redeemed_rewards