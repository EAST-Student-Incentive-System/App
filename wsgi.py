import click, pytest, sys
from flask.cli import with_appcontext, AppGroup
from flask import Blueprint, jsonify, request

from App.database import db, get_migrate
from App.models import User, Student, Staff
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize,
                              get_user, get_user_by_username, update_user, view_profile )
from App.controllers import event, badge, Student
from App.database import db, get_migrate
from App.models import User, Badge
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize, viewProgress, viewLeaderBoard )
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize, createBadge, awardBadge,
                              viewStudentBadges, viewBadges)
from datetime import datetime
from App.views.event import event_views


# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
app.register_blueprint(event_views)
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


@app.cli.command('create-db', help='Create all database tables')
def create_db_command():
    from App.database import create_db
    create_db()
    print('database created')


@app.cli.command('drop-db', help='Drop all database tables')
def drop_db_command():
    db.drop_all()
    print('database dropped')


@app.cli.command('seed', help='Seed the database with initial data')
def seed_command():
    initialize()
    print('database seeded')


@app.cli.command('runserver', help='Run development server')
@click.option('--host', default='127.0.0.1', help='Host to listen on')
@click.option('--port', default=5000, type=int, help='Port to listen on')
@click.option('--debug/--no-debug', default=False, help='Enable debug mode')
def runserver(host, port, debug):
    app.run(host=host, port=port, debug=debug)
'''
Event Commands
'''



@app.cli.command("create_event", help="Creates an event")
@click.argument("staff_id", type=int)
@click.argument("name")
@click.argument("type")
@click.argument("description")
@click.argument("start")
@click.argument("end")
def create_event_command(staff_id, name, type, description, start, end):
    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(end, "%Y-%m-%d %H:%M")
    except ValueError:
        print("Invalid date format. Use 'YYYY-MM-DD HH:MM'.")
        return
    event.create_event(staff_id, name, type, description, start_dt, end_dt)
    print(f'Event {name} created!')

@app.cli.command("update_event", help="Updates an event")
@click.argument("event_id", type=int)
@click.argument("name", required=False)
@click.argument("type", required=False)
@click.argument("description", required=False)
@click.argument("start", required=False)
@click.argument("end", required=False)
def update_event_command(event_id, name, type, description, start, end):
    kwargs = {}
    if name: kwargs['name'] = name
    if type: kwargs['type'] = type
    if description: kwargs['description'] = description
    if start:
        try:
            kwargs['start'] = datetime.strptime(start, "%Y-%m-%d %H:%M")
        except ValueError:
            print("Invalid start date format. Use 'YYYY-MM-DD HH:MM'.")
            return
    if end:
        try:
            kwargs['end'] = datetime.strptime(end, "%Y-%m-%d %H:%M")
        except ValueError:
            print("Invalid end date format. Use 'YYYY-MM-DD HH:MM'.")
            return
    updated_event = event.update_event(event_id, **kwargs)
    if updated_event:
        print(f'Event {event_id} updated!')
    else:
        print(f'Event {event_id} not found.')

@app.cli.command("delete_event", help="Deletes an event")
@click.argument("event_id", type=int)
def delete_event_command(event_id):
    if event.delete_event(event_id):
        print(f'Event {event_id} deleted!')
    else:
        print(f'Event {event_id} not found.')

@app.cli.command("list_events", help="Lists all events")
def list_events_command():
    events = event.view_all_events()
    for evt in events:
        print(f'event {evt.id}: {evt.name} ({evt.type}) from {evt.start} to {evt.end}')

@app.cli.command("list_upcoming_events", help="Lists upcoming events")
def list_upcoming_events_command():
    events = event.view_upcoming_events()
    for evt in events:
        print(evt)

@app.cli.command("event_history", help="Lists event history for a student or staff")
@click.argument("student_id", required=False, type=int)
@click.argument("staff_id", required=False, type=int)
def event_history_command(student_id=None, staff_id=None):
    history = event.view_event_history(student_id=student_id, staff_id=staff_id)
    for record in history:
        print(record)

@app.cli.command("join_event", help="Student joins an event")
@click.argument("student_id", type=int)
@click.argument("event_id", type=int)
def join_event_command(student_id, event_id):
    if event.join_event(student_id, event_id):
        print(f'Student {student_id} joined event {event_id}!')
    else:
        print(f'Failed to join event {event_id}. Check if student and event exist.')

@app.cli.command("log_attendance", help="Logs attendance for a student at an event")
@click.argument("student_id", type=int)
@click.argument("event_id", type=int)   
def log_attendance_command(student_id, event_id):
    if event.log_attendance(student_id, event_id):
        print(f'Attendance logged for student {student_id} at event {event_id}!')
    else:
        print(f'Failed to log attendance for event {event_id}. Check if student and event exist.')

@app.cli.command("generate_qr", help="Generates a QR code for an event")
@click.argument("event_id", type=int)
def generate_qr_command(event_id):
    qr_code = event.generate_qr_code(event_id)
    if qr_code:
        print(f'QR code generated for event {event_id}!: {qr_code}')
    else:
        print(f'Failed to generate QR code for event {event_id}. Check if event exists.')


"""@app.cli.command("scan_qr", help="Scans a QR code for an event and logs attendance")
@click.argument("student_id", type=int)
@click.argument("qr_data")
def scan_qr_command(student_id, qr_data):
    if event.scan_qr_code(student_id, qr_data):
        print(f'QR code scanned and attendance logged for student {student_id}!')
    else:
        print(f'Failed to scan QR code. Check if student exists and QR data is valid.')
""" # will implement later when QR code scanning is set up on the frontend

progress_cli = AppGroup('progress', help='Progress controller commands') 

@progress_cli.command("view", help="View progress for a student")
@click.argument("student_id", type=int)
def view_progress_command(student_id):
    progress = viewProgress(student_id)
    if progress:
        total_points, current_balance = progress
        print(f'Student {student_id} - Total Points: {total_points}, Current Balance: {current_balance}')
    else:
        print(f'Student {student_id} not found.')

@progress_cli.command("leaderboard", help="View Leaderboard")
def view_leaderboard_command(): 
    leaderboard = viewLeaderBoard()
    print("Leaderboard:")
    for entry in leaderboard:
        print(f"Rank {entry['rank']}: {entry['username']} - Total Points: {entry['total_points']}")

app.cli.add_command(progress_cli)
'''
Badge Commands
'''

badge_cli = AppGroup('badge', help='Badge object commands') 

@badge_cli.command("create", help="Creates a badge")
@click.argument("name")
@click.argument("description")
@click.argument("points_required", type=int)
def create_user_command(name, description, points_required):
    badge = createBadge(name, description, points_required)
    if badge is not None:
        print(f'Badge {badge.name} created!')
    else:
        print(f'Failed to create badge. A badge with the name "{name}" already exists.')

@badge_cli.command("award", help="Awards a badge to a student")
@click.argument("student_id", type=int)
@click.argument("badge_id", type=int)
def award_badge_command(student_id, badge_id):
    awarded = awardBadge(student_id, badge_id)
    if awarded:
        print(f'Badge {badge_id} awarded to student {student_id}!')
    else:
        print(f'Failed to award {badge_id} to student {student_id}. Student may not meet requirements or badge may already be awarded.')

app.cli.add_command(badge_cli)

@badge_cli.command("view_all", help='View all badges in the system')
def view_badges_command():
    badges = viewBadges()
    for badge in badges:
        print(badge)

@badge_cli.command("view_student", help="View badges earned by a student")
@click.argument("student_id", type=int)
def view_student_badges_command(student_id):
    badges = viewStudentBadges(student_id)
    if badges:                      
        print(f'Badges earned by student {student_id}:')
        for badge in badges:
            print(badge)
    else:
        print(f'Student {student_id} has not earned any badges or does not exist.')

