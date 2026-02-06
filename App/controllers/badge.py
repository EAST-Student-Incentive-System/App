from App.models import Badge
from App.models import Student
from App.database import db

def awardBadge(student_id, badge_id):
    student = Student.query.get(student_id)
    badge = Badge.query.get(badge_id)

    if badge and student:
        if badge not in student.badges:
            student.badges.append(badge)
            db.session.commit()
            return True
    return False