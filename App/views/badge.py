from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.models.student import Student
from App.controllers import badge

# ✅ Blueprint name matches url_for("badge_views....")
badge_views = Blueprint("badge_views", __name__, template_folder="../templates")


@badge_views.route("/badges/create", methods=["POST"])
@jwt_required()
def create_badge_route():
    data = request.json or {}
    points_required = data.get("points_required", data.get("pointsRequired"))

    if points_required is None:
        return jsonify({"error": "points_required is required"}), 400

    new_badge = badge.createBadge(
        data.get("name"),
        data.get("description"),
        int(points_required),
    )

    if new_badge is not None:
        return jsonify(new_badge.get_json()), 201
    return jsonify({"error": "Badge with this name already exists"}), 400


@badge_views.route("/badges/award", methods=["POST"])
@jwt_required()
def award_badge_route():
    data = request.json or {}
    student_id = get_jwt_identity()
    badge_id = data.get("badge_id")

    if badge_id is None:
        return jsonify({"error": "badge_id is required"}), 400

    success = badge.awardBadge(student_id=student_id, badge_id=int(badge_id))
    if success:
        return jsonify({"message": "Badge awarded successfully"}), 200
    return jsonify({"error": "Failed to award badge"}), 400


@badge_views.route("/badges", methods=["GET"])
@jwt_required()
def view_badges_route():
    badges = badge.viewBadges() or []
    return jsonify([b.get_json() for b in badges]), 200


@badge_views.route("/badges/student/<int:student_id>", methods=["GET"])
@jwt_required()
def view_student_badges_route(student_id):
    badges = badge.viewStudentBadges(student_id) or []
    return jsonify([b.get_json() for b in badges]), 200


@badge_views.route("/student/badges", methods=["GET"])
@jwt_required()
def student_badges_sections_page():
    user_id = get_jwt_identity()
    student = Student.query.get(user_id)

    if not student or student.role != "student":
        flash("Unauthorized", "error")
        return redirect(url_for("auth_views.login_page"))

    all_badges = badge.viewBadges() or []
    earned_badge_ids = set(link.badge_id for link in (student.student_badges or []))

    FEATURED_KEYWORDS = ("workshop", "presentation", "career", "cultural", "competition")
    WEEKLY_KEYWORDS = ("week", "weekly", "streak", "7", "14", "30")

    def icon_for(name: str) -> str:
        n = (name or "").lower()
        if "workshop" in n: return "🛠️"
        if "presentation" in n: return "🎤"
        if "attendance" in n or "attend" in n or "semester" in n: return "📅"
        if "cultural" in n: return "🎭"
        if "competition" in n or "champion" in n: return "🏆"
        if "health" in n or "wellness" in n: return "💪"
        if "career" in n: return "💼"
        return "🏅"

    def section_for(name: str) -> str:
        n = (name or "").lower()
        if any(k in n for k in WEEKLY_KEYWORDS):
            return "weekly"
        if any(k in n for k in FEATURED_KEYWORDS):
            return "featured"
        return "all"

    featured_badges, weekly_badges, rest_badges = [], [], []

    for b in all_badges:
        data = b.get_json()  # expects id,name,description,pointsRequired
        data["earned"] = data.get("id") in earned_badge_ids
        data["icon"] = icon_for(data.get("name"))
        pr = data.get("pointsRequired") or 0
        data["pct"] = int(min(100, (student.current_balance / pr) * 100)) if pr else 0
        data["isNew"] = False

        sec = section_for(data.get("name", ""))
        if sec == "featured":
            featured_badges.append(data)
        elif sec == "weekly":
            weekly_badges.append(data)
        else:
            rest_badges.append(data)

    key_fn = lambda x: (not x.get("earned", False), x.get("pointsRequired", 0))
    featured_badges.sort(key=key_fn)
    weekly_badges.sort(key=key_fn)
    rest_badges.sort(key=key_fn)

    return render_template(
        "student_badges_sections.html",
        user=student,
        balance=student.current_balance,
        featured_badges=featured_badges[:8],
        weekly_badges=weekly_badges[:8],
        all_badges=rest_badges,
    )