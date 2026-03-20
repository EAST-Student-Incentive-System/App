from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user, get_jwt_identity
from App.models import Student, user
from App.models.staff import Staff
from App import db

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


@user_views.route('/students/<int:student_id>/history', methods=['GET'])
@jwt_required()
def student_history_page(student_id):
    user_id = get_jwt_identity()
    user = Student.query.get(user_id)
    history = get_student_history(student_id)
    if history is None:
        return "Student not found", 404
    return render_template('student_history.html', history=history, user=user)

# --------------------------------------------------
# Staff command endpoints
# --------------------------------------------------

@user_views.route('/staff/flagged', methods=['GET'])
@jwt_required()
def flagged_command():   
    user_id = get_jwt_identity()
    user = Staff.query.get(user_id)
    print (user_id, user)
    if not user or not user.role == "staff":
        return jsonify({'error': 'Unauthorized'}), 403
    return render_template('staff_flagged.html', user=user, flagged_students=Student.query.filter_by(isFlagged=True).all())

@user_views.route('/staff/flagged/<int:student_id>/unflag', methods=['POST'])
@jwt_required()
def unflag_student(student_id):
    user_id = get_jwt_identity()
    user = Staff.query.get(user_id)
    if not user or not user.role == "staff":
        return jsonify({'error': 'Unauthorized'}), 403
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    student.isFlagged = False
    db.session.commit()
    flash(f"Student {student.username} has been unflagged.")
    print (f"Unflagged student {student.username} (ID: {student.id})" f" by staff {user.username} (ID: {user.id})")
    return redirect(url_for(endpoint='user_views.flagged_command'))

"""@user_views.route('/staff/flagged/<int:student_id>/timeout', methods=['POST'])
@jwt_required()
def timeout_student(student_id):
    user_id = get_jwt_identity()
    user = Staff.query.get(user_id)
    if not user or not user.role == "staff":
        return jsonify({'error': 'Unauthorized'}), 403
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    student.isFlagged = False
    student.timeout_until = datetime.now() + timedelta(days=7)  # Timeout for 30 minutes
    db.session.commit()
    flash(f"Student {student.username} has been timed out for 30 minutes.")
    print (f"Timed out student {student.username} (ID: {student.id})" f" by staff {user.username} (ID: {user.id})")
    return redirect(url_for(endpoint='user_views.flagged_command'))"""  #add column timeout_until to Student model to use this function, add logic to display device info if that was suspicious activity that led to the timeout