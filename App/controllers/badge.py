from App.models import Badge
from App.models import Student, StudentBadge
from App.database import db
from sqlalchemy.exc import IntegrityError
from App.utils import require_role


def _student_has_badge(student_id: int, badge_id: int) -> bool:
    return (
        db.session.query(StudentBadge.id)
        .filter(StudentBadge.user_id == student_id, StudentBadge.badge_id == badge_id)
        .first()
        is not None
    )


# Controller function to award a badge to a student (POINTS-BASED: milestones only)
def awardBadge(student_id, badge_id):
    student = Student.query.get(student_id)
    badge = Badge.query.get(badge_id)

    if not badge or not student:
        return False

    # NEW: don't auto-award event_type badges by points
    if getattr(badge, "type", "milestone") != "milestone":
        return False

    if badge.points_required <= student.total_points:
        if not _student_has_badge(student_id, badge_id):
            link = StudentBadge(user_id=student_id, badge_id=badge_id)
            db.session.add(link)
            db.session.commit()
            return True

    return False


def awardTestBadge(student_id, badge_id, earned_at):
    student = Student.query.get(student_id)
    badge = Badge.query.get(badge_id)

    if not badge or not student:
        return False

    # NEW: don't auto-award event_type badges by points
    if getattr(badge, "type", "milestone") != "milestone":
        return False

    if badge.points_required <= student.total_points:
        if not _student_has_badge(student_id, badge_id):
            link = StudentBadge(user_id=student_id, badge_id=badge_id, earned_at=earned_at)
            db.session.add(link)
            db.session.commit()
            return True

    return False


# NEW: award event_type badges explicitly (call this from event check-in logic)
def awardEventTypeBadge(student_id, badge_id=None, badge_name=None):
    student = Student.query.get(student_id)
    if not student:
        return False

    if badge_id is not None:
        badge = Badge.query.get(badge_id)
    elif badge_name is not None:
        badge = Badge.query.filter_by(name=badge_name).first()
    else:
        return False

    if not badge:
        return False

    if getattr(badge, "type", "milestone") != "event_type":
        return False

    if _student_has_badge(student_id, badge.id):
        return False

    link = StudentBadge(user_id=student_id, badge_id=badge.id)
    db.session.add(link)

    try:
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False
    
def check_and_award_badges(student, event):
    """
    Called inside log attendance after points are added.
    Decides which badges the student is eligible for.
    """
    # 1. Award milestone badges (points-based)
    milestone_badges = Badge.query.filter_by(type="milestone").all()
    for badge in milestone_badges:
        awardBadge(student.id, badge.id)

    # 2. Award event-type badges (explicit)
    event_type_badges = Badge.query.filter_by(type="event_type").all()
    for badge in event_type_badges:
        # You can filter by event type/name if needed
        if badge.name.lower() == event.type.lower():
            awardEventTypeBadge(student.id, badge.id)


# Controller function to view all badges in the system
def viewBadges():
    badges = Badge.query.all()
    return badges

# Controller function to view badges earned by a specific student
def viewStudentBadges(student_id):
    student = require_role(student_id, "student")
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