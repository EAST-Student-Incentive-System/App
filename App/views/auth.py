from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies

from App.database import db
from App.models import Student, Staff
from.index import index_views

from App.controllers import (
    login, create_user, get_all_users_json, get_user,
    get_user_by_username, update_user, signUp, change_password, send_verification_email
)
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request
from App.models import User
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from flask import current_app


auth_views = Blueprint('auth_views', __name__, template_folder='../templates')




'''
Page/Action Routes
'''    

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")

@auth_views.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        data = request.form
        result = signUp(data['email'], data['username'], data['password'])
        if 'error' in result:
            flash(result['error'])
        else:
            flash(f"Account created for {result['user']['username']} as {result['user']['role']}")
            flash("Please check your email to verify your account before logging in. Email may be in junk/spam folder.")
            return redirect(url_for('auth_views.login_page'))
    return render_template('signup.html', title="Sign Up")

@auth_views.route('/login', methods=['GET'])
def login_page():
    try:
        user_id = get_jwt_identity()   # will raise if no/expired token
        if user_id:
            user = User.query.get(user_id)
            if user.role == 'staff':
                return redirect(url_for('event_views.get_staff_events_route'))
            if user.role == 'student':
                return redirect(url_for('event_views.get_student_events_route'))
    except Exception:
        # no valid token, fall through to login page
        pass

    #  Always render login form if not authenticated
    return render_template('login.html')


from flask_jwt_extended import set_access_cookies

@auth_views.route('/login/action', methods=['POST'])
def login_action():
    data = request.form
    result = login(data['username'], data['password'], data.get('device_id'))

    if 'error' in result:
        flash(result['error'], 'danger')
        return redirect(url_for('auth_views.login_page'))

    token = result.get('access_token')
    role = result.get('role')

    if role == 'staff':
        response = redirect(url_for('event_views.get_staff_events_route')) 
    elif role == 'student':
        response = redirect(url_for('event_views.get_student_events_route'))
    else:
        response = redirect(url_for('index_views.index_page')) 
    set_access_cookies(response, token)   # <-- attach JWT to cookie
    return response


@auth_views.route('/logout', methods=['GET'])
def logout_action():
    response = redirect('/login')
    flash("Logged Out!")
    unset_jwt_cookies(response)
    return response #redirect to login page


@auth_views.route("/verify")
def verify_email():
    token = request.args.get("token")
    user = db.session.execute(db.select(User).filter_by(verification_token=token)).scalar_one_or_none()

    if user and user.token_expiry > datetime.utcnow():
        user.is_verified = True
        user.verification_token = None
        user.token_expiry = None
        db.session.commit()
        flash("Your email has been verified!", "success")
        return redirect(url_for("auth_views.login_page"))
    else:
        flash("Verification link is invalid or expired.", "error")
        return redirect(url_for("auth_views.resend_verification_page"))
    


@auth_views.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password_page():
    if request.method == 'POST':
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Email not found", "error")
            return redirect(url_for("auth_views.forgot_password_page"))

        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = serializer.dumps(email, salt="password-reset-salt")
        reset_url = f"{current_app.config['BASE_URL']}/reset-password?token={token}"

        message = Mail(
            from_email="no-reply@yourapp.com",
            to_emails=email,
            subject="Password Reset Request",
            html_content=f"Click <a href='{reset_url}'>here</a> to reset your password."
        )
        sg = SendGridAPIClient(current_app.config['SENDGRID_API_KEY'])
        sg.send(message)

        flash("Password reset link sent to your email.", "success")
        return redirect(url_for("auth_views.login_page"))

    return render_template('forgot_password.html', title="Forgot Password")


@auth_views.route("/reset-password", methods=["GET","POST"])
def reset_password_page():
    token = request.args.get("token")
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=3600)
    except Exception:
        flash("Invalid or expired token", "error")
        return redirect(url_for("auth_views.forgot_password_page"))

    if request.method == "POST":
        new_password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(new_password)
            db.session.commit()
            flash("Password updated successfully!", "success")
            return redirect(url_for("auth_views.login_page"))

    return render_template("reset_password.html", email=email)


'''
API Routes
'''

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
  data = request.json
  token = login(data['username'], data['password'])
  if not token:
    return jsonify(message='bad username or password given'), 401
  response = jsonify(access_token=token) 
  set_access_cookies(response, token)
  return response

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    return jsonify({'message': f"username: {current_user.username}, id : {current_user.id}"})

@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response

# User API routes
@auth_views.route('/api/users', methods=['GET'])
def api_get_all_users():
    """Get all users"""
    users = get_all_users_json()
    return jsonify(users)

@auth_views.route('/api/users/<int:user_id>', methods=['GET'])
def api_get_user(user_id):
    """Get user by ID"""
    user = get_user(user_id)
    if user:
        return jsonify(user.get_json())
    return jsonify({'error': 'User not found'}), 404

@auth_views.route('/api/users/username/<username>', methods=['GET'])
def api_get_user_by_username(username):
    """Get user by username"""
    user = get_user_by_username(username)
    if user:
        return jsonify(user.get_json())
    return jsonify({'error': 'User not found'}), 404

@auth_views.route('/api/users', methods=['POST'])
def api_create_user():
    """Create a user (auto-determines role based on email domain)"""
    data = request.json
    if not data:
        return jsonify({'error': 'Missing JSON body'}), 400
    try:
        user = create_user(data['email'], data['username'], data['password'])
        return jsonify({'message': f"user {user.username} created as {user.role}", 'user': user.get_json()}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@auth_views.route('/api/users/<int:user_id>', methods=['PUT'])
def api_update_user(user_id):
    """Update user"""
    data = request.json
    if not data:
        return jsonify({'error': 'Missing JSON body'}), 400
    success = update_user(user_id, data.get('username'))
    if success:
        user = get_user(user_id)
        if not user:
            return jsonify({'error': 'User not found after update'}), 404
        return jsonify({'message': 'User updated', 'user': user.get_json()})
    return jsonify({'error': 'User not found'}), 404

# Staff API routes
@auth_views.route('/api/staff', methods=['GET'])
def api_get_all_staff():
    """Get all staff members"""
    staff = db.session.scalars(db.select(Staff)).all()
    return jsonify([s.get_json() for s in staff])

@auth_views.route('/api/staff/<int:staff_id>', methods=['GET'])
def api_get_staff(staff_id):
    """Get staff member by ID"""
    staff = db.session.get(Staff, staff_id)
    if staff:
        return jsonify(staff.get_json())
    return jsonify({'error': 'Staff member not found'}), 404

@auth_views.route('/api/staff', methods=['POST'])
def api_create_staff():
    """Create a staff member"""
    data = request.json
    if not data:
        return jsonify({'error': 'Missing JSON body'}), 400
    try:
        if not data['email'].endswith('@sta.uwi.edu'):
            return jsonify({'error': 'Staff email must end with @sta.uwi.edu'}), 400
        staff = Staff(email=data['email'], username=data['username'], password=data['password'])
        db.session.add(staff)
        db.session.commit()
        return jsonify({'message': f"staff {staff.username} created", 'staff': staff.get_json()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Student API routes
@auth_views.route('/api/students', methods=['GET'])
def api_get_all_students():
    """Get all students"""
    students = db.session.scalars(db.select(Student)).all()
    return jsonify([s.get_json() for s in students])

@auth_views.route('/api/students/<int:student_id>', methods=['GET'])
def api_get_student(student_id):
    """Get student by ID"""
    student = db.session.get(Student, student_id)
    if student:
        return jsonify(student.get_json())
    return jsonify({'error': 'Student not found'}), 404

@auth_views.route('/api/students', methods=['POST'])
def api_create_student():
    """Create a student"""
    data = request.json
    if not data:
        return jsonify({'error': 'Missing JSON body'}), 400
    try:
        if not data['email'].endswith('@my.uwi.edu'):
            return jsonify({'error': 'Student email must end with @my.uwi.edu'}), 400
        student = Student(email=data['email'], username=data['username'], password=data['password'])
        db.session.add(student)
        db.session.commit()
        return jsonify({'message': f"student {student.username} created", 'student': student.get_json()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@auth_views.route('/api/students/<int:student_id>/points', methods=['POST'])
def api_add_student_points(student_id):
    """Add points to student"""
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    data = request.json
    if not data:
        return jsonify({'error': 'Missing JSON body'}), 400
    amount = data.get('amount')
    if not amount or amount <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
    
    student.add_points(amount)
    db.session.commit()
    return jsonify({'message': 'Points added', 'student': student.get_json()})

@auth_views.route('/api/students/<int:student_id>/redeem', methods=['POST'])
def api_redeem_student_points(student_id):
    """Redeem points from student"""
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    data = request.json
    if not data:
        return jsonify({'error': 'Missing JSON body'}), 400
    amount = data.get('amount')
    if not amount or amount <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
    
    success = student.subtract_points(amount)
    db.session.commit()
    
    if success:
        return jsonify({'message': 'Points redeemed', 'student': student.get_json()})
    return jsonify({'error': 'Insufficient points'}), 400