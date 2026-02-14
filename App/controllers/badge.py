from App.models import Badge
from App.models import Student, StudentBadge
from App.database import db
from sqlalchemy.exc import IntegrityError

# Controller function to award a badge to a student
def awardBadge(student_id, badge_id):
    student = Student.query.get(student_id)
    badge = Badge.query.get(badge_id)

    if badge and student:
        if badge.points_required <= student.total_points:
            if badge not in student.student_badges:
                link = StudentBadge(user_id=student_id, badge_id=badge_id)
                db.session.add(link)
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
        return student.student_badges
    return []

# Controller function to create a new badge
def createBadge(name, description, points_required):
    new_badge = Badge(name=name, description=description, points_required=points_required)
    try:
        db.session.add(new_badge)
        db.session.commit()
        return new_badge
    except IntegrityError as e:
        db.session.rollback()
        return None