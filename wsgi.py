import click, pytest, sys
from flask.cli import with_appcontext, AppGroup
from App.controllers import event
from App.database import db, get_migrate
from App.models import User
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize, viewProgress )
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
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    create_user(username, password)
    print(f'{username} created!')

# this command will be : flask user create bob bobpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli) # add the group to the cli

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

app.cli.add_command(progress_cli)
