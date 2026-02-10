from App.models import User, Student, Staff
from App.database import db

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