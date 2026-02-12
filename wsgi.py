import click, pytest, sys
from flask.cli import with_appcontext, AppGroup
from flask import Blueprint, jsonify, request

from App.database import db, get_migrate
from App.models import User, Student, Staff
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize,
                              get_user, get_user_by_username, update_user, view_profile )


# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
    print('database intialized')

'''
User Commands
'''

# Commands can be organized using groups

# create a group, it would be the first argument of the comand
# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands') 

# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("email", default="user@my.uwi.edu")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(email, username, password):
    try:
        user = create_user(email, username, password)
        print(f'{username} created as {user.role}!')
    except ValueError as e:
        print(f'Error: {e}')

# this command will be : flask user create user@my.uwi.edu bob bobpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

@user_cli.command("get", help="Get user by ID")
@click.argument("user_id", type=int)
def get_user_command(user_id):
    user = get_user(user_id)
    if user:
        print(user.get_json())
    else:
        print(f"User with ID {user_id} not found")

@user_cli.command("get_by_username", help="Get user by username")
@click.argument("username")
def get_user_by_username_command(username):
    user = get_user_by_username(username)
    if user:
        print(user.get_json())
    else:
        print(f"User {username} not found")

@user_cli.command("update", help="Update user username")
@click.argument("user_id", type=int)
@click.argument("new_username")
def update_user_command(user_id, new_username):
    result = update_user(user_id, new_username)
    if result:
        print(f"User {user_id} updated to {new_username}")
    else:
        print(f"User {user_id} not found")

app.cli.add_command(user_cli) # add the group to the cli

'''
Staff Commands
'''

staff_cli = AppGroup('staff', help='Staff object commands')

@staff_cli.command("create", help="Creates a staff member")
@click.argument("email")
@click.argument("username")
@click.argument("password")
def create_staff_command(email, username, password):
    try:
        if not email.endswith('@sta.uwi.edu'):
            print("Error: Staff email must end with @sta.uwi.edu")
            print("Would you like to auto-correct the email? (y/n)")
            choice = input().lower()
            if choice == 'y':
                email = email.split('@')[0] + '@sta.uwi.edu'
                print(f"Email corrected to {email}")
            else:
                return
        staff = Staff(email=email, username=username, password=password)
        db.session.add(staff)
        db.session.commit()
        print(f'Staff {username} created with ID {staff.id}!')
    except Exception as e:
        db.session.rollback()
        print(f'Error creating staff: {e}')

@staff_cli.command("list", help="Lists all staff members")
def list_staff_command():
    staff_members = db.session.scalars(db.select(Staff)).all()
    if staff_members:
        for staff in staff_members:
            print(staff)
    else:
        print("No staff members found")

@staff_cli.command("get", help="Get staff member by ID")
@click.argument("staff_id", type=int)
def get_staff_command(staff_id):
    staff = db.session.get(Staff, staff_id)
    if staff:
        print(staff.get_json())
    else:
        print(f"Staff with ID {staff_id} not found")

app.cli.add_command(staff_cli)

'''
Student Commands
'''

student_cli = AppGroup('student', help='Student object commands')

@student_cli.command("create", help="Creates a student")
@click.argument("email")
@click.argument("username")
@click.argument("password")
def create_student_command(email, username, password):
    try:
        if not email.endswith('@my.uwi.edu'):
            print("Error: Student email must end with @my.uwi.edu")
            print("Would you like to auto-correct the email? (y/n)")
            choice = input().lower()
            if choice == 'y':
                email = email.split('@')[0] + '@my.uwi.edu'
                print(f"Email corrected to {email}")
            else:
                return
        student = Student(email=email, username=username, password=password)
        db.session.add(student)
        db.session.commit()
        print(f'Student {username} created with ID {student.id}!')
    except Exception as e:
        db.session.rollback()
        print(f'Error creating student: {e}')

@student_cli.command("list", help="Lists all students")
def list_student_command():
    students = db.session.scalars(db.select(Student)).all()
    if students:
        for student in students:
            print(student)
    else:
        print("No students found")

@student_cli.command("get", help="Get student by ID")
@click.argument("student_id", type=int)
def get_student_command(student_id):
    student = db.session.get(Student, student_id)
    if student:
        print(student.get_json())
    else:
        print(f"Student with ID {student_id} not found")

@student_cli.command("add_points", help="Add points to a student")
@click.argument("student_id", type=int)
@click.argument("amount", type=int)
def add_points_command(student_id, amount):
    student = db.session.get(Student, student_id)
    if student:
        student.add_points(amount)
        db.session.commit()
        print(f"Added {amount} points to {student.username}. New balance: {student.current_balance}")
    else:
        print(f"Student with ID {student_id} not found")

@student_cli.command("subtract_points", help="Subtract points from a student")
@click.argument("student_id", type=int)
@click.argument("amount", type=int)
def subtract_points_command(student_id, amount):
    student = db.session.get(Student, student_id)
    if student:
        success = student.subtract_points(amount)
        if success:
            db.session.commit()
            print(f"Subtracted {amount} points from {student.username}. New balance: {student.current_balance}")
        else:
            print(f"Insufficient points. Current balance: {student.current_balance}")
    else:
        print(f"Student with ID {student_id} not found")

app.cli.add_command(student_cli)

'''
API Routes
'''

api_blueprint = Blueprint('api', __name__, url_prefix='/api')

# User API routes
@api_blueprint.route('/users', methods=['GET'])
def api_get_all_users():
    """Get all users"""
    users = get_all_users_json()
    return jsonify(users)

@api_blueprint.route('/users/<int:user_id>', methods=['GET'])
def api_get_user(user_id):
    """Get user by ID"""
    user = get_user(user_id)
    if user:
        return jsonify(user.get_json())
    return jsonify({'error': 'User not found'}), 404

@api_blueprint.route('/users/username/<username>', methods=['GET'])
def api_get_user_by_username(username):
    """Get user by username"""
    user = get_user_by_username(username)
    if user:
        return jsonify(user.get_json())
    return jsonify({'error': 'User not found'}), 404

@api_blueprint.route('/users', methods=['POST'])
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

@api_blueprint.route('/users/<int:user_id>', methods=['PUT'])
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
@api_blueprint.route('/staff', methods=['GET'])
def api_get_all_staff():
    """Get all staff members"""
    staff = db.session.scalars(db.select(Staff)).all()
    return jsonify([s.get_json() for s in staff])

@api_blueprint.route('/staff/<int:staff_id>', methods=['GET'])
def api_get_staff(staff_id):
    """Get staff member by ID"""
    staff = db.session.get(Staff, staff_id)
    if staff:
        return jsonify(staff.get_json())
    return jsonify({'error': 'Staff member not found'}), 404

@api_blueprint.route('/staff', methods=['POST'])
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
@api_blueprint.route('/students', methods=['GET'])
def api_get_all_students():
    """Get all students"""
    students = db.session.scalars(db.select(Student)).all()
    return jsonify([s.get_json() for s in students])

@api_blueprint.route('/students/<int:student_id>', methods=['GET'])
def api_get_student(student_id):
    """Get student by ID"""
    student = db.session.get(Student, student_id)
    if student:
        return jsonify(student.get_json())
    return jsonify({'error': 'Student not found'}), 404

@api_blueprint.route('/students', methods=['POST'])
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

@api_blueprint.route('/students/<int:student_id>/points', methods=['POST'])
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

@api_blueprint.route('/students/<int:student_id>/redeem', methods=['POST'])
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

app.register_blueprint(api_blueprint)

'''
Test Commands
'''

test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))
    

app.cli.add_command(test)