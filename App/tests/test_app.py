import os, tempfile, pytest, logging, unittest
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
    student = create_user("stu@my.uwi.edu", "stu", "pwd")
    history = get_student_history(student.id)
    assert history is not None
    assert history['student']['username'] == 'stu'
    assert history['badges'] == []
    assert history['events'] == []
    assert history['rewards'] == []


def test_authenticate():
    # create a student using valid email domain
    user = create_user("bob@my.uwi.edu", "bob", "bobpass")
    assert login("bob", "bobpass") != None

class UsersIntegrationTests(unittest.TestCase):

    def test_create_user(self):
        # create a student record
        user = create_user("rick@my.uwi.edu", "rick", "bobpass")
        assert user.username == "rick"

    def test_get_all_users_json(self):
        users_json = get_all_users_json()
        # returned data now includes email/role/points - just verify expected students present
        usernames = sorted([u.get('username') for u in users_json])
        self.assertIn('bob', usernames)
        self.assertIn('rick', usernames)

    # Tests data changes in the database
    def test_update_user(self):
        update_user(1, "ronnie")
        user = get_user(1)
        assert user.username == "ronnie"
        

