from App.models import Event, Attendance, Student, Staff
from App.database import db
from datetime import datetime
import qrcode
import io
import base64


def get_event(event_id):
    return db.session.get(Event, event_id)

def view_upcoming_events():
    now = datetime.now()
    return Event.query.filter(Event.start > now).all()

def view_all_events():
    return Event.query.all()

def view_event_history(student_id=None, staff_id=None):
    if student_id:
        student = db.session.get(Student, student_id)
        return student.attendances
    if staff_id:
        staff = db.session.get(Staff, staff_id)
        return staff.events
    return []

# ---------------- Event CRUD ----------------

def create_event(staff_id, name, type, description, start, end):
    new_event = Event(name=name, type=type, description=description, start=start, end=end)
    new_event.staffId = staff_id
    db.session.add(new_event)
    db.session.commit()
    return new_event

def update_event(event_id, name=None, type=None, description=None, start=None, end=None):
    event = db.session.get(Event, event_id)
    if not event:
        return None
    event.name = name if name else event.name
    event.type = type if type else event.type
    event.description = description if description else event.description
    event.start = start if start else event.start
    event.end = end if end else event.end
    db.session.commit()
    return event

def delete_event(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        return False
    db.session.delete(event)
    db.session.commit()
    return True

# ---------------- Student Event Actions ----------------

def join_event(student_id, event_id):
    student = db.session.get(Student, student_id)
    event = db.session.get(Event, event_id)
    if not student or not event:
        return None
    if student in event.students:
        return False
    if event.closed:
        return False
    event.students.append(student)
    db.session.commit()
    return True

def log_attendance(student_id, event_id):
    student = db.session.get(Student, student_id)
    event = db.session.get(Event, event_id)
    if not student or not event:
        return None
    if student not in event.students:
        return False
    if not event.isWithintTimeFrame():
        return False
    attendance = Attendance(student_id=student_id, event_id=event_id)
    db.session.add(attendance)
    db.session.commit()
    return attendance

# ---------------- QR Code & Attendance Management ----------------

def generate_qr_code(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        return None
    qr = qrcode.QRCode(box_size=10, border=5)
    qr.add_data(f'event:{event_id}')
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return qr_data  # you can embed this in HTML

def close_attendance(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        return None
    if datetime.now() == event.end:
        event.closed = True
    db.session.commit()
    return event


