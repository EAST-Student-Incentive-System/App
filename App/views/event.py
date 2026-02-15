from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.database import db
from App.models.event import Event
from App.models.student import Student
from App.models.staff import Staff
from App.models.attendance import Attendance
from App.controllers import event  # import your controller functions

event_views = Blueprint("event_views", __name__)

# ---------------- Event CRUD ----------------

@event_views.route("/events", methods=["POST"])
@jwt_required()
def create_event_route():
    data = request.json
    staff_id = get_jwt_identity()  # assumes staff is logged in
    new_event = event.create_event(
        staff_id=staff_id,
        name=data["name"],
        type=data["type"],
        description=data["description"],
        start=data["start"],
        end=data["end"]
    )
    return jsonify(new_event), 201

@event_views.route("/events/<int:event_id>", methods=["PUT"])
@jwt_required()
def update_event_route(event_id):
    data = request.json
    updated = event.update_event(event_id, **data)
    if not updated:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(updated), 200

@event_views.route("/events/<int:event_id>", methods=["DELETE"])
@jwt_required()
def delete_event_route(event_id):
    deleted = event.delete_event(event_id)
    if not deleted:
        return jsonify({"error": "Event not found"}), 404
    return jsonify({"message": "Event deleted"}), 200

@event_views.route("/events/upcoming", methods=["GET"])
@jwt_required()
def view_upcoming_events_route():
    events = event.view_upcoming_events()
    return jsonify([e.get_json() for e in events]), 200

@event_views.route("/events", methods=["GET"])
@jwt_required()
def view_all_events_route():
    events = event.view_all_events()
    return jsonify([e.get_json() for e in events]), 200

# ---------------- Student Event Actions ----------------

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

# ---------------- QR Code ----------------

@event_views.route("/events/<int:event_id>/qr", methods=["GET"])
@jwt_required()
def generate_qr_code_route(event_id):
    qr_data = event.generate_qr_code(event_id)
    if not qr_data:
        return jsonify({"error": "Event not found"}), 404
    return jsonify({"qr_code": qr_data}), 200
