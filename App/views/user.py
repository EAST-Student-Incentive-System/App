from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user, get_jwt_identity
from App.controllers.user import update_username, update_password
from App.models import Student, Staff
from App.database import db
from datetime import datetime, timedelta

from.index import index_views

from App.controllers import (
    create_user,
    get_all_users,
    get_all_users_json,
    jwt_required,
    get_student_history
)

user_views = Blueprint('user_views', __name__, template_folder='../templates')

@user_views.route('/users', methods=['GET'])
def get_user_page():
    users = get_all_users()
    return render_template('users.html', users=users)

@user_views.route('/users', methods=['POST'])
def create_user_action():
    data = request.form
    flash(f"User {data['username']} created!")
    create_user(data['username'], data['password'])
    return redirect(url_for('user_views.get_user_page'))

@user_views.route('/api/users', methods=['GET'])
def get_users_action():
    users = get_all_users_json()
    return jsonify(users)

@user_views.route('/api/users', methods=['POST'])
def create_user_endpoint():
    data = request.json
    user = create_user(data['username'], data['password']) # pyright: ignore[reportOptionalSubscript]
    return jsonify({'message': f"user {user.username} created with id {user.id}"})

@user_views.route('/static/users', methods=['GET'])
def static_user_page():
  return send_from_directory('static', 'static-user.html')


# --------------------------------------------------
# Student history endpoints
# --------------------------------------------------

@user_views.route('/api/students/<int:student_id>/history', methods=['GET'])
def student_history_api(student_id):
    history = get_student_history(student_id)
    if history is None:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify(history)


@user_views.route('/students/<int:student_id>/profile', methods=['GET'])
@jwt_required()
def profile_page(student_id):
    user_id = get_jwt_identity()
    user = Student.query.get(user_id)
    history = get_student_history(student_id)
    if history is None:
        return "Student not found", 404
    return render_template('student_profile.html', history=history, user=user)

@user_views.route('/profile/regenerate-avatar', methods=['POST'])
@jwt_required()
def regenerate_avatar():
    jwt_current_user.regenerate_avatar()
    db.session.commit()
    flash('New profile picture generated!', 'success')
    return redirect(url_for('user_views.profile_page', student_id=jwt_current_user.id))

@user_views.route('/profile/update-username', methods=['POST'])
@jwt_required()
def update_username_route():
    new_username = request.form.get('username', '').strip()
    success, message = update_username(jwt_current_user.id, new_username)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('user_views.profile_page', student_id=jwt_current_user.id))

@user_views.route('/profile/update-password', methods=['POST'])
@jwt_required()
def update_password_route():
    current_password = request.form.get('current_password', '')
    new_password     = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    if new_password != confirm_password:
        flash("New passwords do not match.", 'danger')
        return redirect(url_for('user_views.profile_page', student_id=jwt_current_user.id))

    success, message = update_password(jwt_current_user.id, current_password, new_password)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('user_views.profile_page', student_id=jwt_current_user.id))


#-----------------------Staff flagging endpoints-----------------------
@user_views.route("/staff/flagged", methods=["GET"], endpoint="flagged_command")
@jwt_required()
def flagged_command():
    staff_id = get_jwt_identity()
    staff = db.session.get(Staff, int(staff_id)) if staff_id else None
    if not staff or staff.role != "staff":
        flash("Unauthorized", "error")
        return redirect(url_for("auth_views.login_page"))

    # Query flagged students
    flagged_students = db.session.scalars(
        db.select(Student).where(Student.isFlagged == True)
    ).all()

    return render_template("staff_flagged.html", flagged_students=flagged_students, user=staff)

@user_views.route("/staff/flagged/<int:student_id>/unflag", methods=["POST"])
@jwt_required()
def unflag_student(student_id):
    staff_id = get_jwt_identity()
    staff = db.session.get(Staff, int(staff_id)) if staff_id else None
    if not staff or staff.role != "staff":
        flash("Unauthorized", "error")
        return redirect(url_for("auth_views.login_page"))

    student = db.session.get(Student, student_id)
    if not student:
        flash("Student not found", "error")
        return redirect(url_for("user_views.flagged_command"))

    student.isFlagged = False
    db.session.commit()

    flash(f"{student.username} has been unflagged.", "success")
    return redirect(url_for("user_views.flagged_command"))


@user_views.route("/staff/flagged/<int:student_id>/timeout", methods=["POST"])
@jwt_required()
def timeout_student(student_id):
    staff_id = get_jwt_identity()
    staff = db.session.get(Staff, int(staff_id)) if staff_id else None
    if not staff or staff.role != "staff":
        flash("Unauthorized", "error")
        return redirect(url_for("auth_views.login_page"))

    student = db.session.get(Student, student_id)
    if not student:
        flash("Student not found", "error")
        return redirect(url_for("user_views.flagged_command"))

    # Apply timeout and unflag
    student.timeout_count = int(student.timeout_count or 0) + 1
    if student.timeout_count >= 3:
        student.timeout_until = datetime.utcnow() + timedelta(days=365 * 100)  # Effectively permanent timeout
    else:
        student.timeout_until = datetime.utcnow() + timedelta(days=7)  # Example: 30 minute timeout
    student.isFlagged = False
    db.session.commit()

    flash(f"{student.username} has been timed out and removed from flagged list.", "success")
    return redirect(url_for("user_views.flagged_command"))
