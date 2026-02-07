from App.models import Student
from App.database import db

def viewProgress(studentId): 
    student = db.session.get(Student, studentId)
    if not student:
        return None
    return student.total_points, student.current_balance

def viewLeaderBoard():
    students = Student.query.order_by(Student.total_points.desc(), Student.username.asc()).all()
    leaderboard = []
    rank = 1
    for student in students:
        leaderboard.append({
            'rank': rank,
            'student_id': student.id,
            'username': student.username,
            'total_points': student.total_points
        })
        rank += 1
    return leaderboard