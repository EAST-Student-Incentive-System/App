from App.models import Badge
from App.models import Student
from App.database import db

# Controller function to award a badge to a student
def awardBadge(student_id, badge_id):
    student = Student.query.get(student_id)
    badge = Badge.query.get(badge_id)

    if badge and student:
        if badge.points_required <= student.total_points:
            if badge not in student.badges:
                student.badges.append(badge)
                db.session.commit()
                return True
    return False

# Controller function to view all badges in the system
def viewBadges():
    badges = Badge.query.all()
    return [badge.get_json() for badge in badges]

# Controller function to view badges earned by a specific student
def viewStudentBadges(student_id):
    student = Student.query.get(student_id)
    if student:
        return [badge.get_json() for badge in student.badges]
    return []