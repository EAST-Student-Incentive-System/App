from App.models import Student
from App.database import db

def viewProgress(studentId): 
    student = db.session.get(Student, studentId)
    if not student:
        return None
    return student.total_points, student.current_balance