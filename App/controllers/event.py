from App.models.event import Event
from App.models import Attendance, Student, Staff
from App.models.student_event import student_event
from App.database import db
from datetime import datetime
import qrcode
import io
import base64
import time
from geopy.distance import geodesic



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
        return Event.query.filter_by(staffId=staff_id).all()
    return []

# ---------------- Event CRUD ----------------

def create_event(staff_id, name, type, description, start, end, location, image, active, limit=None):
    new_event = Event(staffId=staff_id, name=name, type=type, description=description, start=start, end=end, location=location, image=image, active=active, limit=limit)
    db.session.add(new_event)
    db.session.flush()
    #new_event.qr = generate_qr_code(new_event.id)  # Generate QR code data for the event
    db.session.commit()
    return new_event

def update_event(event_id, **kwargs):
    event = db.session.get(Event, event_id)
    if not event:
        return None

    allowed_fields = {
        'name': 'name',
        'type': 'type',
        'description': 'description',
        'start': 'start',
        'end': 'end',
        'location': 'location',
        'image': 'image',
        'active': 'active',
        'limit': 'limit',
    }

    for key, value in kwargs.items():
        if key in allowed_fields and value is not None:
            setattr(event, allowed_fields[key], value)

    db.session.commit()
    return event.get_json()

def delete_event(event_id, staff_id):
    event = db.session.get(Event, event_id)

    print("EVENT:", event)
    print("EVENT STAFF ID:", event.staffId if event else None)
    print("JWT STAFF ID:", staff_id)

    if not event:
        return False

    if int(event.staffId) != int(staff_id):
        print("STAFF ID MISMATCH")
        return False

    db.session.delete(event)
    db.session.commit()
    print("EVENT DELETED FROM DB")
    return True

# ---------------- Student Event Actions ----------------
def join_event(student_id, event_id):
    student = db.session.get(Student, student_id)
    event = db.session.get(Event, event_id)
    count = db.session.query(student_event).filter_by(event_id=event_id).count()
    if not student or not event:
        return None
    if student in event.students:
        return False
    if event.limit and count >= event.limit:
        print("Event is full", "error")
        return False
    event.students.append(student)
    db.session.commit()
    return True  

def leave_event(student_id, event_id):
    db.session.execute(
        student_event.delete().where(
            (student_event.c.student_id == student_id) &
            (student_event.c.event_id == event_id)
        )
    )
    db.session.commit()
    return True

def log_attendance(student_id, event_id, student_lat=None, student_lon=None):
    student = db.session.get(Student, student_id)
    print("STUDENT:", student)
    event = db.session.get(Event, event_id)
    print("EVENT:", event)
    if not student or not event:
        return None
    if student not in event.students:
        return False
    if datetime.now() < event.start:
        print("EVENT NOT STARTED")
        return False
    existing = Attendance.query.filter_by(student_id=student_id, event_id=event_id).first()
    if existing:
        print("ATTENDANCE ALREADY LOGGED")
        return False
    if student_lat and student_lon:
        print("STUDENT LOCATION:", student_lat, student_lon)
        student.temporary_gps_holder = f"{student_lat},{student_lon}"
    if student_lat and student_lon and event.latitude and event.longitude:
        student_coords = (student_lat, student_lon)
        event_coords = (event.latitude, event.longitude)
        distance = geodesic(student_coords, event_coords).meters
        if distance > event.radius:
            db.session.commit()
            return False
    student.add_points(event.calculate_point_value())
    attendance = Attendance(student_id=student_id, event_id=event_id)
    print("NEW ATTENDANCE:", attendance)
    db.session.add(attendance)
    db.session.commit()
    return attendance.get_json()

import pytz

def get_participant_count(event_id, cutoff=None):
    query = db.session.query(student_event).filter(
        student_event.c.event_id == event_id
    )
    if cutoff:
        # assume staff input is local AST (UTC-4)
        local = pytz.timezone("America/Port_of_Spain")
        cutoff_local = local.localize(cutoff)
        cutoff_utc = cutoff_local.astimezone(pytz.utc).replace(tzinfo=None)
        query = query.filter(student_event.c.joined_at <= cutoff_utc)
    return query.count()




# ---------------- QR Code & Attendance Management ----------------

def generate_qr(event_id):
    timestamp = int(time.time() / 30)

    data = f"event:{event_id}|t:{timestamp}"

    qr = qrcode.QRCode(box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    qr_data = base64.b64encode(buffer.getvalue()).decode()

    return qr_data

