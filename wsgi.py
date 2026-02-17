import click, pytest, sys
from flask.cli import with_appcontext, AppGroup

from App.database import db, get_migrate
from App.models import User
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize )
from App.controllers.rewards import (
    create_reward, get_reward, get_all_rewards, get_all_rewards_json,
    get_active_rewards, update_reward, delete_reward, toggle_reward,
    redeem_reward, viewReward, viewRewardHistory
)


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
Reward Commands
'''

reward_cli = AppGroup('reward', help='Reward object commands')


@reward_cli.command("create", help="Create a reward")
@click.argument("name")
@click.argument("description")
@click.argument("point_cost", type=int)
@click.option("--active/--inactive", default=True)
def create_reward_command(name, description, point_cost, active):
    r = create_reward(name, description, point_cost, active=active)
    print('Created reward:', r.get_json() if hasattr(r, 'get_json') else r)


@reward_cli.command("get", help="Get a reward by id")
@click.argument("reward_id", type=int)
def get_reward_command(reward_id):
    r = get_reward(reward_id)
    print(r.get_json() if r else f'No reward with id {reward_id}')


@reward_cli.command("list", help="List all rewards")
@click.argument("format", default="string")
def list_rewards_command(format):
    if format == 'string':
        print(get_all_rewards())
    else:
        print(get_all_rewards_json())


@reward_cli.command("active", help="List active rewards (JSON)")
def active_rewards_command():
    rewards = get_active_rewards()
    print([r.get_json() for r in rewards] if rewards else [])


@reward_cli.command("update", help="Update a reward")
@click.argument("reward_id", type=int)
@click.option("--name", default=None)
@click.option("--description", default=None)
@click.option("--point-cost", type=int, default=None)
@click.option("--active", type=bool, default=None)
def update_reward_command(reward_id, name, description, point_cost, active):
    kwargs = {}
    if name is not None:
        kwargs['name'] = name
    if description is not None:
        kwargs['description'] = description
    if point_cost is not None:
        kwargs['point_cost'] = point_cost
    if active is not None:
        kwargs['active'] = active
    r = update_reward(reward_id, **kwargs)
    print(r.get_json() if r else f'No reward with id {reward_id}')


@reward_cli.command("delete", help="Delete a reward")
@click.argument("reward_id", type=int)
def delete_reward_command(reward_id):
    ok = delete_reward(reward_id)
    print('Deleted' if ok else f'No reward with id {reward_id}')


@reward_cli.command("toggle", help="Toggle a reward active state")
@click.argument("reward_id", type=int)
def toggle_reward_command(reward_id):
    r = toggle_reward(reward_id)
    print(r.get_json() if r else f'No reward with id {reward_id}')


@reward_cli.command("redeem", help="Redeem a reward for a student")
@click.argument("student_id", type=int)
@click.argument("reward_id", type=int)
def redeem_reward_command(student_id, reward_id):
    res = redeem_reward(student_id, reward_id)
    if res is None:
        print('Student or reward not found')
    elif res is False:
        print('Not redeemable or insufficient balance')
    else:
        print('Redeemed:', res.id if hasattr(res, 'id') else res)


@reward_cli.command("view", help="View rewards for a student (redeemable flag)")
@click.argument("student_id", type=int)
def view_rewards_for_student(student_id):
    res = viewReward(student_id)
    print(res if res is not None else f'No student with id {student_id}')


@reward_cli.command("history", help="View rewards created by a staff member")
@click.argument("staff_id", type=int)
def reward_history_command(staff_id):
    res = viewRewardHistory(staff_id)
    print(res if res is not None else f'No rewards for staff id {staff_id}')


app.cli.add_command(reward_cli)

