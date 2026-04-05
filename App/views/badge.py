from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.models.student import Student
from App.controllers import badge
from datetime import datetime

badge_views = Blueprint("badge_views", __name__, template_folder="../templates")


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
    success = badge.awardBadge(student_id=student_id, badge_id=badge_id)
    if success:
        return jsonify({"message": "Badge awarded successfully"}), 200
    return jsonify({"error": "Failed to award badge"}), 400


@badge_views.route("/badges", methods=["GET"])
@jwt_required()
def view_badges_route():
    badges = badge.viewBadges()
    return jsonify([b.get_json() for b in badges]), 200


@badge_views.route("/badges/student/<int:student_id>", methods=["GET"])
@jwt_required()
def view_student_badges_route(student_id):
    badges = badge.viewStudentBadges(student_id)
    return jsonify([b.get_json() for b in badges]), 200


# ✅ ADD THIS: Student badges page (Jinja template)
from datetime import datetime, timedelta
@badge_views.route("/student/badges", methods=["GET"])
@jwt_required()
def student_badges_sections_page():
    user_id = get_jwt_identity()
    student = Student.query.get(user_id)

    if student.timeout_until and student.timeout_until > datetime.utcnow():
        flash(f"You are currently timed out until {student.timeout_until}.", "error")
        return redirect(url_for('appeal_views.student_appeal_page'))

    if not student or student.role != "student":
        flash("Unauthorized", "error")
        return redirect(url_for("auth_views.login_page"))

    all_badges = badge.viewBadges() or []
    earned_badge_ids = set(link.badge_id for link in (student.student_badges or []))

    def icon_for(name: str) -> str:
        n = (name or "").lower()
        if "workshop" in n: return "🛠️"
        if "social" in n: return "🎤"
        if "seminar" in n: return "📚"
        if "volunteer" in n: return "🤝"
        if "time" in n: return "📅"
        if "master" in n: return "🌟"
        if "champion" in n: return "🏆"
        if "king" in n: return "👑"
        if "legend" in n: return "🦸"
        if "rookie" in n: return "👶"
        return "🏅"

    # Weekly = earned in last 7 days
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_badges = []
    for link in student.student_badges:
        if link.earned_at and link.earned_at >= one_week_ago:
            data = link.badge.get_json()
            data["earned"] = True
            data["icon"] = icon_for(data.get("name"))
            pr = data.get("pointsRequired") or 0
            data["pct"] = int(min(100, (student.current_balance / pr) * 100)) if pr else 0
            weekly_badges.append(data)

    # All badges (show everything in the system)
    all_badges_data = []
    for b in all_badges:
        data = b.get_json()
        data["earned"] = b.id in earned_badge_ids
        data["icon"] = icon_for(data.get("name"))
        pr = data.get("pointsRequired") or 0
        data["pct"] = int(min(100, (student.current_balance / pr) * 100)) if pr else 0
        all_badges_data.append(data)


    earned_badges = [b for b in all_badges_data if b["earned"]]

    return render_template(
        "student_badges_sections.html",
        user=student,
        balance=student.total_points,
        earned_badges=earned_badges,
        weekly_badges=weekly_badges,
        all_badges=all_badges_data
    )

#------------------------------------------
# API endpoints for Performance Testing or backend use (not meant for frontend/Jinja consumption)
#------------------------------------------

# Create a new badge
@badge_views.route("/api/badges", methods=["POST"])
@jwt_required()
def api_create_badge():
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    new_badge = badge.createBadge(
        name=data.get("name"),
        description=data.get("description"),
        points_required=data.get("points_required")
    )
    if new_badge:
        return jsonify(new_badge.get_json()), 201
    return jsonify({"error": "Badge with this name already exists"}), 400


# Award a badge to the current student
@badge_views.route("/api/badges/award", methods=["POST"])
@jwt_required()
def api_award_badge():
    data = request.json
    if not data or "badge_id" not in data:
        return jsonify({"error": "Missing badge_id"}), 400
    student_id = get_jwt_identity()
    success = badge.awardBadge(student_id=student_id, badge_id=int(data["badge_id"]))
    if success:
        return jsonify({"success": True, "message": "Badge awarded successfully"}), 200
    return jsonify({"error": "Failed to award badge"}), 400


# View all badges in the system
@badge_views.route("/api/badges", methods=["GET"])
@jwt_required()
def api_view_badges():
    badges = badge.viewBadges()
    return jsonify([b.get_json() for b in badges]), 200


# View badges owned by a specific student
@badge_views.route("/api/badges/student/<int:student_id>", methods=["GET"])
@jwt_required()
def api_view_student_badges(student_id):
    badges = badge.viewStudentBadges(student_id)
    return jsonify([b.get_json() for b in badges]), 200


# View badges for the current student (earned, weekly, all)
@badge_views.route("/api/student/badges", methods=["GET"])
@jwt_required()
def api_student_badges_sections():
    user_id = get_jwt_identity()
    student = Student.query.get(user_id)
    if not student or student.role != "student":
        return jsonify({"error": "Unauthorized"}), 403

    all_badges = badge.viewBadges() or []
    earned_badge_ids = set(link.badge_id for link in (student.student_badges or []))

    one_week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_badges = []
    for link in student.student_badges:
        if link.earned_at and link.earned_at >= one_week_ago:
            data = link.badge.get_json()
            data["earned"] = True
            weekly_badges.append(data)

    all_badges_data = []
    for b in all_badges:
        data = b.get_json()
        data["earned"] = b.id in earned_badge_ids
        all_badges_data.append(data)

    earned_badges = [b for b in all_badges_data if b["earned"]]

    return jsonify({
        "student_id": student.id,
        "balance": student.total_points,
        "earned_badges": earned_badges,
        "weekly_badges": weekly_badges,
        "all_badges": all_badges_data
    }), 200

