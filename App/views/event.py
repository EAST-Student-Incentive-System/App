from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.database import db
from App.models.event import Event
from App.controllers import event  # import your controller functions
from App.models.student import Student
from App.models.staff import Staff
from App.models.student_event import student_event
from App.models.attendance import Attendance
from App.controllers import event
from App.controllers.event import log_attendance  # import your controller functions
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app, abort, Flask
from App.controllers.event import join_event,get_participant_count # import your controller functions
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from App.models import User
from App.database import db
from werkzeug.utils import secure_filename
from App.controllers.event import generate_qr
from os import path, makedirs
import os
import secrets
from geopy.distance import geodesic

event_views = Blueprint("event_views", __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'App/static/uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------- Event CRUD ----------------

# ---------- CREATE EVENT ----------
@event_views.route("/events/new", methods=["GET","POST"])
@jwt_required()
def create_event_route():
    user_id = get_jwt_identity()
    user = Staff.query.get(user_id)
    if not user or user.role != 'staff':
        flash('Unauthorized', 'error')
        return redirect(url_for('event_views.get_staff_events_route'))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        type_ = request.form.get("type")
        start_str = request.form.get("start")
        end_str = request.form.get("end")
        location = request.form.get("location")
        image = request.files.get("image")
        active = bool(request.form.get("active"))

        if not all([name, description, start_str, end_str, location, type_]):
            flash('All fields are required', 'error')
            return redirect(url_for('event_views.get_staff_events_route'))

        try:
            start_dt = datetime.strptime(start_str, "%Y-%m-%dT%H:%M")
            end_dt = datetime.strptime(end_str, "%Y-%m-%dT%H:%M")

            new_event = Event(
                staffId=user.id,
                name=name,
                type=type_,
                description=description,
                start=start_dt,
                end=end_dt,
                location=location,
                active = active
            )

            # Handle image upload safely
            if image and image.filename:
                print("Received image file:", image.filename)
                filename = secure_filename(image.filename)
                upload_folder = os.path.join(current_app.static_folder, "uploads")
                os.makedirs(upload_folder, exist_ok=True)  # ensure folder exists
                filepath = os.path.join(upload_folder, filename)
                image.save(filepath)
                new_event.image = filename

            
            db.session.add(new_event)
            db.session.flush()  # flush to get ID
            #new_event.qr = generate_qr_code(new_event.id)

            print("Image file:", image)
            print("Filename:", filename if image else None)

            db.session.commit()
            flash('Event created successfully!', 'success')
            return redirect(url_for('event_views.get_staff_events_route'))

        except ValueError as e:
            flash(f"Error: {e}", 'error')
            return redirect(url_for('event_views.get_staff_events_route'))
        

    return render_template("edit_event.html", event=None)

# ---------- UPDATE EVENT ----------
@event_views.route("/events/<int:event_id>", methods=["GET","POST"])
@jwt_required()
def update_event_route(event_id):
    user_id = get_jwt_identity()
    user = Staff.query.get(user_id)
    if not user or user.role != 'staff':
        flash('Unauthorized', 'error')
        return redirect(url_for('event_views.get_staff_events_route'))

    event_obj = Event.query.get(event_id)
    if not event_obj:
        flash('Event not found', 'error')
        return redirect(url_for('event_views.get_staff_events_route'))

    if request.method == "POST":
        print("FILES RECEIVED:", request.files)
        print("FORM DATA:", request.form)
        name = request.form.get("name")
        description = request.form.get("description")
        type_ = request.form.get("type")
        start_str = request.form.get("start")
        end_str = request.form.get("end")
        location = request.form.get("location")
        image_file = request.files.get("image")
        active = bool(request.form.get("active"))

        if not all([name, description, start_str, end_str, location, type_]):
            flash('All fields are required', 'error')
            return redirect(url_for('event_views.update_event_route', event_id=event_id))

        try:
            start_dt = datetime.strptime(start_str, "%Y-%m-%dT%H:%M")
            end_dt = datetime.strptime(end_str, "%Y-%m-%dT%H:%M")

            event_obj.name = name
            event_obj.description = description
            event_obj.type = type_
            event_obj.start = start_dt
            event_obj.end = end_dt
            event_obj.location = location
            #event_obj.qr = generate_qr_code(event_obj.id)
            event_obj.active = active
            

            image_file = request.files.get("image")

            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                upload_folder = os.path.join(current_app.static_folder, "uploads")
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                image_file.save(filepath)

                event_obj.image = filename  # replace only if new image uploaded
# else → do nothing, keep existing image

            print("Saved image name in DB:", event_obj.image)
            db.session.commit()
            flash('Event updated successfully!', 'success')
            return redirect(url_for('event_views.get_staff_events_route'))

        except ValueError as e:
            flash(f"Error updating event: {e}", 'error')
            return redirect(url_for('event_views.update_event_route', event_id=event_id))
    

    return render_template("edit_event.html", event=event_obj, user=user)

@event_views.route("/events/<int:event_id>/delete", methods=["POST"])
@jwt_required()
def delete_event_route(event_id):
    print("DELETE ROUTE HIT")
    user_id = int(get_jwt_identity())  # <-- cast here

    ok = event.delete_event(event_id, user_id)

    if not ok:
        flash('Event not found or unauthorized', 'error')
    else:
        flash('Event deleted', 'success')

    return redirect(url_for('event_views.get_staff_events_route'))
    

@event_views.route("/events/staff", methods=["GET"])
@jwt_required()
def get_staff_events_route():
    user_id = get_jwt_identity()
    user = Staff.query.get(user_id)
    if not user or user.role != 'staff':
        flash('Unauthorized', 'error')
        return redirect(url_for('event_views.view_upcoming_events_route'))
    staff_id = user.id
    events = event.view_event_history(staff_id=staff_id)
    print("DEBUG: Events for staff_id", staff_id, "=", [e.name for e in events])
    return render_template("staff_events.html", events=events, staff=user, user=user)

@event_views.route("/events/<int:event_id>/filter_participants", methods=["POST"])
@jwt_required()
def filter_participants(event_id):
    print("FILTER PARTICIPANTS ROUTE HIT")
    participant_count = get_participant_count(event_id)
    cutoff_str = request.form.get("cutoff")
    print("Participant count for event_id", event_id, "=", participant_count)

    event = Event.query.get_or_404(event_id)

    rows = db.session.query(student_event).filter(
    student_event.c.event_id == event_id).all()

    for r in rows:
        print("DEBUG row:", r.student_id, r.event_id, r.joined_at)
        event = Event.query.get_or_404(event_id)
        cutoff_str = request.form.get("cutoff")

    if cutoff_str:
        cutoff = datetime.fromisoformat(cutoff_str)
        participant_count = get_participant_count(event_id, cutoff)

    print("Filtered participant count for event_id", event_id, "with cutoff", cutoff_str, "=", participant_count)

    return render_template(
        "edit_event.html",
        event=event,
        participant_count=participant_count,
        cutoff=cutoff,
        user = Staff.query.get(get_jwt_identity())
    )



@event_views.route("/events/<int:event_id>/attendance")
@jwt_required()
def event_qr_page(event_id):
    user_id = get_jwt_identity()
    user = Staff.query.get(user_id)
    if not user or user.role != 'staff':
        flash('Unauthorized', 'error')
        return redirect(url_for('event_views.get_staff_events_route'))
    event = Event.query.get(event_id)

    if not event:
        return "Event not found", 404
    
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    radius = request.args.get("radius", type=int, default=200)

    event.latitude = lat
    event.longitude = lon
    event.radius = radius
    db.session.commit()
    print("Updated event with GPS:", event.latitude, event.longitude, "radius:", event.radius)

    qr = generate_qr(event_id)

    return render_template(
        "attendance_qr.html",
        event=event,
        qr=qr,
        user=user
    )

# ---------------- Student Event Actions ----------------
@event_views.route("/events/student", methods=["GET"])
@jwt_required()
def get_student_events_route():
    print("STUDENT EVENTS ROUTE HIT")
    user_id = get_jwt_identity()
    user = Student.query.get(user_id)
    if not user or user.role != 'student':
        print("Unauthorized access attempt by user_id:", user_id)
        flash('Unauthorized', 'error')
        return redirect(url_for('auth_views.login_page'))
    student_id = user.id
    events = Event.query.filter_by(active=True).all()
    print("DEBUG: Events for student_id", student_id, "=", [e.name for e in events])
    return render_template("student_event.html", events=events, student=user, user=user)

@event_views.route("/events/upcoming", methods=["GET"])
@jwt_required()
def view_upcoming_events_route():
    events = event.view_upcoming_events()
    return jsonify([e.get_json() for e in events]), 200

@event_views.route("/api/events/student", methods=["GET"])
@jwt_required()
def view_all_events_route():
    events = event.view_all_events()
    return jsonify([e.get_json() for e in events]), 200

@event_views.route("/api/events/<int:event_id>/join", methods=["POST"])
@jwt_required()
def join_event_route(event_id):

    student_id = get_jwt_identity()

    joined = event.join_event(student_id, event_id)

    if joined is None:
        return jsonify({"error": "Invalid student or event"}), 404

    if joined is False:
        return jsonify({"message": "Student already joined"}), 400

    return jsonify({"message": "Student joined event"}), 200


@event_views.route("/events/<int:event_id>/join", methods=["POST"])
@jwt_required()
def join_event_action(event_id):
    user_id = get_jwt_identity()
    user = Student.query.get(user_id)
    if not user or user.role != 'student':
        flash('Unauthorized', 'error')
        return redirect(url_for('auth_views.login_page'))
    student_id = user.id
    joined = join_event(student_id, event_id)   # <-- call the function, not event.join_event
    if joined:
        flash("You’ve joined this event!")
    else:
        flash("Already joined or invalid event.")
    return redirect(url_for("event_views.get_student_events_route"))


@event_views.route("/events/<int:event_id>/attendance/<int:student_id>", methods=["POST"])
@jwt_required()
def log_attendance_route(event_id, student_id):
    attendance = event.log_attendance(student_id, event_id)
    if attendance is None:
        return jsonify({"error": "Invalid student or event"}), 404
    if attendance is False:
        return jsonify({"message": "Attendance not valid"}), 400
    return jsonify(attendance), 201

@event_views.route("/attendance/log")
@jwt_required()
def log_attendance_qr():
    raw_event_id = request.args.get("event_id")

    # Handle QR codes like "event:12|t:59108539"
    event_id = None
    if raw_event_id:
        if raw_event_id.startswith("event:"):
            try:
                event_id = int(raw_event_id.split("|")[0].split(":")[1])
            except ValueError:
                event_id = None
        else:
            try:
                event_id = int(raw_event_id)
            except ValueError:
                event_id = None

    user_id = get_jwt_identity()
    user = Student.query.get(user_id)
    if not user or user.role != 'student':
        flash('Unauthorized', 'error')
        return redirect(url_for('auth_views.login_page'))
    

    # Get GPS values from query string
    student_lat = request.args.get("lat", type=float)
    student_lon = request.args.get("lon", type=float)

    event = Event.query.get(event_id)
    if not event:
        flash("Event not found", "error")
        return redirect(url_for("event_views.get_student_events_route"))

    # Save attempted GPS in student record
    if student_lat and student_lon:
        user.temporary_gps_holder = f"{student_lat},{student_lon}"

    # GPS check
    if not student_lat or not student_lon:
        print("No GPS data provided")
    
    if student_lat and student_lon and event.latitude and event.longitude:
        print("Checking GPS for attendance...")
        student_coords = (student_lat, student_lon)
        event_coords = (event.latitude, event.longitude)
        distance = geodesic(student_coords, event_coords).meters
        print(">>> Distance from event:", distance)

        if distance > event.radius:
            flash("Wrong location — outside attendance radius", "warning")
            return redirect(url_for("event_views.get_student_events_route"))

    student_id = user.id
    attendance = log_attendance(student_id, event_id)

    if attendance is None:
        flash("Invalid student or event", "error")
    elif attendance is False:
        flash("Attendance not valid", "warning")
    else:
        flash("Attendance logged successfully!", "success")

    return redirect(url_for("event_views.get_student_events_route"))


@event_views.route("/scan", methods=["GET"])
@jwt_required()
def scan_qr_page():
    user_id = get_jwt_identity()
    user = Student.query.get(user_id)
    if not user or user.role != 'student':
        flash('Unauthorized', 'error')
        return redirect(url_for('auth_views.login_page'))
    return render_template("scan_qr.html", user=user)










