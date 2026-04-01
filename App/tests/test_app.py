import re
import os, tempfile, pytest, logging, unittest
from turtle import st
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import User
from App.controllers import (
    create_user,
    get_all_users_json,
    login,
    get_user,
    get_user_by_username,
    update_user,
    get_student_history
)
from App.models.reward import Reward
from App.models.staff import Staff
from App.models.student import Student


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UserUnitTests(unittest.TestCase):

    def test_new_user(self):
        # email, username, password
        user = User("bob@example.com", "bob", "bobpass")
        assert user.username == "bob"

    # pure function no side effects or integrations called
    def test_get_json(self):
        user = User("bob@example.com", "bob", "bobpass")
        user_json = user.get_json()
        # email is part of the json now; role defaults to 'user'
        self.assertDictEqual(user_json, {"id":None, "email":"bob@example.com", "username":"bob", "role":"user"})
    
    def test_hashed_password(self):
        password = "mypass"
        hashed = generate_password_hash(password)
        user = User("bob@example.com", "bob", password)
        assert user.password != password

    def test_check_password(self):
        password = "mypass"
        user = User("bob@example.com", "bob", password)
        assert user.check_password(password)
        
class StudentUnitTests(unittest.TestCase):
    
    def test_new_student(self):
        student: Student = create_user("student1@my.uwi.edu", "student1", "studentpass")
        assert student.username == "student1"

    def test_student_add_points(self):
        student: Student = create_user("student2@my.uwi.edu", "student2", "studentpass") # type: ignore
        # Test adding points to the student
        student.add_points(100)
        assert student.current_balance == 100

    def test_student_subtract_points(self):
        student: Student = create_user("student3@my.uwi.edu", "student3", "studentpass") # type: ignore
        # Test subtracting points from the student
        student.add_points(100)
        student.subtract_points(50)
        assert student.current_balance == 50

    def test_check_enough_points_success(self):
        student: Student = create_user("student4@my.uwi.edu", "student4", "studentpass") # type: ignore
        student.add_points(100)
        reward2 = Reward("Test Reward2", 50, pointCost=50)  # reward name and cost
        assert student.check_enough_points(reward2)

    def test_check_enough_points_failure(self):
        student: Student = create_user("student5@my.uwi.edu", "student5", "studentpass") # type: ignore
        student.add_points(100)
        reward = Reward("Test Reward", 150, pointCost=150)  # reward name and cost
        assert not student.check_enough_points(reward) # This should return False since the student doesn't have enough points. Hence the assertion should be that the result is False.


'''
    Integration Tests
'''

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    # keep an application context for the duration of the tests
    ctx = app.app_context()
    ctx.push()
    create_db()
    yield app.test_client()
    db.drop_all()
    ctx.pop()


def test_student_history_controller():
    # ensure history returns empty arrays for a fresh student
    student = create_user("stu2@my.uwi.edu", "stu2", "pwd")
    history = get_student_history(student.id)
    assert history is not None
    assert history['student']['username'] == 'stu2'
    assert history['badges'] == []
    assert history['events'] == []
    assert history['rewards'] == []


def test_authenticate():
    # create a student using valid email domain
    user = create_user("bob2@my.uwi.edu", "bob2", "bobpass")
    assert login("bob2", "bobpass") != None

class UsersIntegrationTests(unittest.TestCase):

    def test_create_user(self):
        # create a student record
        user = create_user("rick2@my.uwi.edu", "rick2", "bobpass")
        assert user.username == "rick2"

    def test_get_all_users_json(self):
        users_json = get_all_users_json()
        # returned data now includes email/role/points - just verify expected students present
        usernames = sorted([u.get('username') for u in users_json])
        self.assertIn('bob2', usernames)
        self.assertIn('rick2', usernames)

    # Tests data changes in the database
    def test_update_user(self):
        update_user(1, "ronnie")
        user = get_user(1)
        assert user.username == "ronnie"
        

