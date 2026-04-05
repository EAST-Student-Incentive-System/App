from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.database import db
from App.controllers import progress
from App.models.student import Student
from datetime import datetime

progress_views = Blueprint("progress_views", __name__)

@progress_views.route("/progress/<int:student_id>", methods=["GET"])
@jwt_required()
def view_progress_route(student_id):
    progress_data = progress.viewProgress(student_id)
    if progress_data:
        total_points, current_balance = progress_data
        return jsonify({"Total Points": total_points, "Current Balance": current_balance}), 200
    else:
        return jsonify({"error": "Student not found"}), 404
    
@progress_views.route("/progress/leaderboard", methods=["GET"])
@jwt_required()
def view_leaderboard_route():
    leaderboard = progress.viewLeaderBoard()
    user_id = get_jwt_identity()
    user = Student.query.get(user_id)

    if user.timeout_until and user.timeout_until > datetime.utcnow():
        flash("You are currently timed out until {}. You cannot access the leaderboard page until this time is up or an appeal is approved.".format(user.timeout_until), "error")
        return redirect(url_for('appeal_views.student_appeal_page'))

    # Build a username -> avatar_seed lookup so the template can render DiceBear avatars
    usernames = [entry['username'] for entry in leaderboard]
    students = Student.query.filter(Student.username.in_(usernames)).all()
    avatar_seeds = {s.username: s.avatar_seed for s in students}

    return render_template(
        "leaderboard.html",
        leaderboard=leaderboard,
        user=user,
        avatar_seeds=avatar_seeds,
    )


#------------------------------------------
# API endpoints for Performance Testing
#------------------------------------------

# View progress for a student
@progress_views.route("/api/progress/<int:student_id>", methods=["GET"])
@jwt_required()
def api_view_progress(student_id):
    progress_data = progress.viewProgress(student_id)
    if progress_data:
        total_points, current_balance = progress_data
        return jsonify({
            "student_id": student_id,
            "total_points": total_points,
            "current_balance": current_balance
        }), 200
    return jsonify({"error": "Student not found"}), 404


# View leaderboard
@progress_views.route("/api/progress/leaderboard", methods=["GET"])
@jwt_required()
def api_view_leaderboard():
    leaderboard = progress.viewLeaderBoard()
    user_id = get_jwt_identity()
    user = Student.query.get(user_id)

    if not user or user.role != "student":
        return jsonify({"error": "Unauthorized"}), 403

    if user.timeout_until and user.timeout_until > datetime.utcnow():
        return jsonify({
            "error": f"Timed out until {user.timeout_until}. Please submit an appeal."
        }), 403

    # Attach avatar seeds for each student
    usernames = [entry['username'] for entry in leaderboard]
    students = Student.query.filter(Student.username.in_(usernames)).all()
    avatar_seeds = {s.username: s.avatar_seed for s in students}

    # Merge avatar seeds into leaderboard entries
    enriched_leaderboard = []
    for entry in leaderboard:
        entry_copy = dict(entry)
        entry_copy["avatar_seed"] = avatar_seeds.get(entry["username"])
        enriched_leaderboard.append(entry_copy)

    return jsonify({
        "leaderboard": enriched_leaderboard,
        "current_user": {
            "id": user.id,
            "username": user.username,
            "avatar_seed": user.avatar_seed
        }
    }), 200


