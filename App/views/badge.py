from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.database import db
from App.models.badge import Badge
from App.models.student import Student
from App.controllers import badge

badge_views = Blueprint("badge_views", __name__)

@badge_views.route("/badges/create", methods=["POST"])
@jwt_required()
def create_badge_route():
    data = request.json
    new_badge = badge.createBadge(
        name=data["name"],
        description=data["description"],
        points_required=data["points_required"]
    )
    if new_badge is not None:
        return jsonify(new_badge.get_json()), 201
    return jsonify({"error": "Badge with this name already exists"}), 400
    

@badge_views.route("/badges/award", methods=["POST"])
@jwt_required()
def award_badge_route():
    data = request.json
    student_id = get_jwt_identity()
    badge_id = int(data["badge_id"])
    success = badge.awardBadge(
        student_id=student_id,
        badge_id=badge_id
    )
    if success:
        return jsonify({"message": "Badge awarded successfully"}), 200
    return jsonify({"error": "Failed to award badge"}), 400

@badge_views.route("/badges", methods=["GET"])
@jwt_required()
def view_badges_route():
    badges = badge.viewBadges()
    return jsonify([badge.get_json() for badge in badges]), 200

@badge_views.route("badges/student/<int:student_id>", methods=["GET"])
@jwt_required()
def view_student_badges_route(student_id):
    badges = badge.viewStudentBadges(student_id)
    return jsonify([badge.get_json() for badge in badges]), 200
