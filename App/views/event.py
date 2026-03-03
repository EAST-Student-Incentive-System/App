from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.database import db
from App.models.event import Event
from App.models.student import Student
from App.models.staff import Staff
from App.models.attendance import Attendance
from App.controllers import event  # import your controller functions
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity

event_views = Blueprint("event_views", __name__)

# ---------------- Event CRUD ----------------

@event_views.route("/events/new", methods=["GET","POST"])
@jwt_required()
def create_event_route():
    user = get_jwt_identity()
    if not user or user.get('role') != 'staff':
        flash('Unauthorized', 'error')
        return redirect(url_for('event_views.get_staff_events_route'))
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        date_str = request.form.get("date")  # Expecting 'YYYY-MM-DD'
        time_str = request.form.get("time")  # Expecting 'HH:MM'
        location = request.form.get("location")

        if not all([name, description, date_str, time_str, location]):
            flash('All fields are required', 'error')
            return redirect(url_for('event_views.get_staff_events_route'))

        try:
            new_event = event.create_event(name, description, date_str, time_str, location)
            flash('Event created successfully!', 'success')
            return redirect(url_for('event_views.get_staff_events_route'))
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('event_views.get_staff_events_route'))
    
    if request.method == "GET":
        return render_template("edit_event.html")
    

@event_views.route("/events/<int:event_id>", methods=["GET","POST"])
@jwt_required()
def update_event_route(event_id):
    user = get_jwt_identity()
    if not user or user.get('role') != 'staff':
        flash('Unauthorized', 'error')
        return redirect(url_for('event_views.get_staff_events_route'))
    r = event.get_event(event_id)
    if not r:
        flash('Event not found', 'error')
        return redirect(url_for('event_views.get_staff_events_route'))
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        date_str = request.form.get("date")  # Expecting 'YYYY-MM-DD'
        time_str = request.form.get("time")  # Expecting 'HH:MM'
        location = request.form.get("location")

        if not all([name, description, date_str, time_str, location]):
            flash('All fields are required', 'error')
            return redirect(url_for('event_views.get_staff_events_route'))

        try:
            event.update_event(event_id, name=name, description=description, date_str=date_str, time_str=time_str, location=location)
            flash('Event updated successfully!', 'success')
            return redirect(url_for('event_views.get_staff_events_route'))
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('event_views.get_staff_events_route'))
        
    if request.method == "GET":
        return render_template("edit_event.html", event=r)
    

@event_views.route("/events/<int:event_id>/delete", methods=["POST"])
@jwt_required()
def delete_event_route(event_id):
    user = get_jwt_identity()
    if not user or user.get('role') != 'staff':
        flash('Unauthorized', 'error')
        return redirect(url_for('event_views.get_staff_events_route'))
    ok = event.delete_event(event_id)
    if not ok:
        flash('Event not found', 'error')
    else:
        flash('Event deleted', 'success')
    return redirect(url_for('event_views.get_staff_events_route'))
    

@event_views.route("/events/staff", methods=["GET"])
@jwt_required()
def get_staff_events_route():
    user = get_jwt_identity()
    if not user or user.get('role') != 'staff':
        flash('Unauthorized', 'error')
        return redirect(url_for('event_views.view_upcoming_events_route'))
    staff_id = user.get('id')
    events = event.view_event_history(staff_id=staff_id)
    events_data = [e.get_json() for e in events]
    return render_template("staff_events.html", events=events_data)


# ---------------- Student Event Actions ----------------
@event_views.route("/events/upcoming", methods=["GET"])
@jwt_required()
def view_upcoming_events_route():
    events = event.view_upcoming_events()
    return jsonify([e.get_json() for e in events]), 200

@event_views.route("/events/student", methods=["GET"])
@jwt_required()
def view_all_events_route():
    events = event.view_all_events()
    return jsonify([e.get_json() for e in events]), 200

@event_views.route("/events/<int:event_id>/join/<int:student_id>", methods=["POST"])
@jwt_required()
def join_event_route(event_id, student_id):
    joined = event.join_event(student_id, event_id)
    if joined is None:
        return jsonify({"error": "Invalid student or event"}), 404
    if joined is False:
        return jsonify({"message": "Student already joined"}), 400
    return jsonify({"message": "Student joined event"}), 200

@event_views.route("/events/<int:event_id>/attendance/<int:student_id>", methods=["POST"])
@jwt_required()
def log_attendance_route(event_id, student_id):
    attendance = event.log_attendance(student_id, event_id)
    if attendance is None:
        return jsonify({"error": "Invalid student or event"}), 404
    if attendance is False:
        return jsonify({"message": "Attendance not valid"}), 400
    return jsonify(attendance), 201

