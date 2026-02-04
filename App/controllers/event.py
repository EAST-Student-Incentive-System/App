from App.models import Event, Attendance, Student, Staff
from App.database import db
from datetime import datetime
import qrcode
import io
import base64


def get_event_history(student_id=None, staff_id=None):
    if student_id:
        student = db.session.get(Student, student_id)
        return student.attendances if student else []
    if staff_id:
        staff = db.session.get(Staff, staff_id)
        return staff.events if staff else []
    return []

def get_event(event_id):
    return db.session.get(Event, event_id)

def get_all_events():
    return db.session.scalars(db.select(Event)).all()


# ---------------- Staff Event Actions ----------------

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
    if name:
        event.set_name(name)
    if type:
        event.set_type(type)
    if description:
        event.set_description(description)
    if start:
        event.set_start(start)
    if end:
        event.set_end(end)
    db.session.commit()
    return event



# ---------------- Student Event Actions ----------------

def enter_event(student_id, event_id):
    student = db.session.get(Student, student_id)
    event = db.session.get(Event, event_id)
    if not student or not event:
        return None
    if student in event.students:
        return False  # already entered
    event.students.append(student)
    db.session.commit()
    return True

def log_attendance(student_id, event_id):
    student = db.session.get(Student, student_id)
    event = db.session.get(Event, event_id)
    if not student or not event:
        return None
    # Ensure within event time
    if not event.isWithintTimeFrame():
        return False
    attendance = Attendance(student_id=student_id, event_id=event_id)
    db.session.add(attendance)
    db.session.commit()
    return attendance

# ---------------- System Event Actions ----------------

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
    return qr_data 

def close_attendance(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        return None
    event.end = datetime.now()
    db.session.commit()
    return event

