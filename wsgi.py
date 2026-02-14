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