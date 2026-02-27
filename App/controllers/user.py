from App.models import User, Student, Staff
from App.database import db

from flask import Blueprint, render_template, request, redirect, url_for, flash
from itsdangerous import URLSafeTimedSerializer

user = Blueprint('user', __name__)
serializer= URLSafeTimedSerializer('your_secret_key')

def create_user(email, username, password):
    if email.endswith('@my.uwi.edu'):
        newuser = Student(email=email, username=username, password=password)
    elif  email.endswith('@sta.uwi.edu'):
        newuser = Staff(email=email, username=username, password=password)
    else:
        raise ValueError("Invalid email domain. Only UWI staff or student emails are allowed.")
    db.session.add(newuser)
    db.session.commit()
    return newuser

def get_user_by_username(username):
    result = db.session.execute(db.select(User).filter_by(username=username))
    return result.scalar_one_or_none()

def get_user(id):
    return db.session.get(User, id)

def get_all_users():
    return db.session.scalars(db.select(User)).all()

def get_all_users_json():
    users = get_all_users()
    if not users:
        return []
    users = [user.get_json() for user in users]
    return users

def update_user(id, username):
    user = get_user(id)
    if user:
        user.username = username
        # user is already in the session; no need to re-add
        db.session.commit()
        return True
    return None

def view_profile(user_id):
    user = get_user(user_id)
    if user:
        return user.get_json()
    print ("User not found")
    return None


@user.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        #test
        print(username, email, password)

        return f"Welcome, {username}!"
    return render_template("login.html")

@user.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        return redirect(url_for("user.login"))

    return render_template("signup.html")


@user.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        
        # check if user exists
        # For demo, generate a token anyway
        token = serializer.dumps(email, salt="password-reset-salt")
        reset_link = url_for('user.reset_password', token=token, _external=True)

        # For test purposes: print the reset link to console
        print(f"[FORGOT PASSWORD] Reset link for {email}: {reset_link}")

        flash("A password reset link has been sent to your email (check console).")
        return redirect(url_for('user.login'))

    return render_template("forgot_password.html")

@user.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=3600)  # 1 hour expiry
    except Exception:
        return "Invalid or expired token", 400

    if request.method == "POST":
        new_password = request.form.get("password")
        # update the user's password in your database
        print(f"[RESET PASSWORD] New password for {email}: {new_password}")
        return redirect(url_for("user.login"))

    return render_template("reset_password.html", email=email)