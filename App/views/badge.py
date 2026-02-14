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
    if new_badge is None:
        return jsonify({"error": "Badge with this name already exists"}), 400
    return jsonify(new_badge.get_json()), 201