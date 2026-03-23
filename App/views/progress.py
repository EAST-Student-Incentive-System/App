from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.database import db
from App.controllers import progress
from App.models.student import Student

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


