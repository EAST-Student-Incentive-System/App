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
    return new_event.get_json()

def update_event(event_id, **kwargs):
    event = db.session.get(Event, event_id)
    if not event:
        return None

    allowed_fields = {
        'name': 'name',
        'type': 'type',
        'description': 'description',
        'start': 'start',
        'end': 'end'
    }

    for key, value in kwargs.items():
        if key in allowed_fields and value is not None:
            setattr(event, allowed_fields[key], value)

    db.session.commit()
    return event.get_json()

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
    if event.start < datetime.now(): #can't join past events
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
    student.add_points(event.calculate_point_value())
    attendance = Attendance(student_id=student_id, event_id=event_id)
    db.session.add(attendance)
    db.session.commit()
    return attendance.get_json()

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

def scan_qr_code(student_id, qr_data):
    if not qr_data.startswith('event:'):
        return None
    try:
        event_id = int(qr_data.split(':')[1])
    except (IndexError, ValueError):
        return None
    return log_attendance(student_id, event_id)


