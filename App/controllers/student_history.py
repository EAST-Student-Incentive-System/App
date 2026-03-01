from App.models import Student, Attendance, RedeemedReward, StudentBadge
from App.database import db


def get_student_history(student_id):
    """Return a combined history object for a student.

    The returned dictionary has the following shape:

        {
            'student': { ... },       # from Student.get_json()
            'badges': [ {...}, ... ],  # list of StudentBadge JSON records
            'events': [ {...}, ... ],  # list of Attendance JSON records
            'rewards': [ {...}, ... ], # list of RedeemedReward JSON records
        }

    If the student does not exist the function returns ``None``.
    """
    student = db.session.get(Student, student_id)
    if not student:
        return None

    badges = [sb.get_json() for sb in student.student_badges]
    events = [att.get_json() for att in student.attendances]

    # also pull redeemed rewards through relationship for convenience
    rewards = [rr.get_json() for rr in student.redeemed_rewards]

    # sort each list chronologically if timestamp/earnedAt/redeemedAt available
    try:
        badges.sort(key=lambda x: x.get('earnedAt'))
    except Exception:
        pass
    try:
        events.sort(key=lambda x: x.get('timestamp'))
    except Exception:
        pass
    try:
        rewards.sort(key=lambda x: x.get('redeemedAt'))
    except Exception:
        pass

    return {
        'student': student.get_json(),
        'badges': badges,
        'events': events,
        'rewards': rewards,
    }
