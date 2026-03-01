from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user

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
    user = create_user(data['username'], data['password'])
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
def student_history_page(student_id):
    history = get_student_history(student_id)
    if history is None:
        return "Student not found", 404
    return render_template('student_history.html', history=history)