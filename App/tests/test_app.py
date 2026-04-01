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
import unittest
from datetime import datetime, timedelta
from App.main import create_app
from App.database import db, create_db
from App.models import Student, Event, Attendance

class AttendanceUnitTests(unittest.TestCase):

    def setUp(self):
        # fresh test app + db
        self.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # create a student + two events
        self.student = Student(email="bob@test.com", username="bob", password="pw")
        self.event1 = Event(staffId=1, name="Event1", type="Social", description="Test",
                            start=datetime.now(), end=datetime.now()+timedelta(hours=2))
        self.event2 = Event(staffId=1, name="Event2", type="Social", description="Test",
                            start=datetime.now(), end=datetime.now()+timedelta(hours=2))
        db.session.add_all([self.student, self.event1, self.event2])
        db.session.commit()

    def tearDown(self):
        db.drop_all()
        self.ctx.pop()

    def test_overlap_events_within_one_hour(self):
        att1 = Attendance(student_id=self.student.id, event_id=self.event1.id, timestamp=datetime.now())
        att2 = Attendance(student_id=self.student.id, event_id=self.event2.id, timestamp=datetime.now()+timedelta(minutes=30))
        db.session.add_all([att1, att2])
        db.session.commit()

        overlaps = att1.get_overlap_events()
        self.assertIn(att2, overlaps)

    def test_device_conflict_same_event_same_device(self):
        student2 = Student(email="alice@test.com", username="alice", password="pw")
        db.session.add(student2)
        db.session.commit()

        att1 = Attendance(student_id=self.student.id, event_id=self.event1.id)
        att1.device_info = "DEVICE123"

        att2 = Attendance(student_id=student2.id, event_id=self.event1.id)
        att2.device_info = "DEVICE123"

        db.session.add_all([att1, att2])
        db.session.commit()

        conflicts = att1.get_device_conflicts()
        self.assertIn(att2, conflicts)



class EventUnitTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.rollback()
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_isWithinTimeFrame_true(self):
        now = datetime.now()
        event = Event(staffId=1, name="TestEvent", type="Social", description="Test",
                      start=now - timedelta(hours=1), end=now + timedelta(hours=1))
        db.session.add(event)
        db.session.commit()
        self.assertTrue(event.isWithintTimeFrame())

    def test_calculate_point_value_rounding(self):
        now = datetime.now()
        # 90 minutes duration → should round up to 2 points
        event = Event(staffId=1, name="TestEvent", type="Social", description="Test",
                      start=now, end=now + timedelta(minutes=90))
        db.session.add(event)
        db.session.commit()
        self.assertEqual(event.calculate_point_value(), 2)

    def test_calculate_point_value_minimum(self):
        now = datetime.now()
        # 10 minutes duration → should still give minimum 1 point
        event = Event(staffId=1, name="ShortEvent", type="Social", description="Test",
                      start=now, end=now + timedelta(minutes=10))
        db.session.add(event)
        db.session.commit()
        self.assertEqual(event.calculate_point_value(), 1)

    def test_check_password(self):
        password = "mypass"
        user = User("bob@example.com", "bob", password)
        assert user.check_password(password)
        
class StudentUnitTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.rollback()
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
    
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

@pytest.fixture
def app_context():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })

    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


def test_student_history_controller(app_context):
    # ensure history returns empty arrays for a fresh student
    student = create_user("stu2@my.uwi.edu", "stu2", "pwd")
    history = get_student_history(student.id)
    assert history is not None
    assert history['student']['username'] == 'stu2'
    assert history['badges'] == []
    assert history['events'] == []
    assert history['rewards'] == []


def test_authenticate(app_context):
    # create a student using valid email domain
    user = create_user("bob2@my.uwi.edu", "bob2", "bobpass")
    assert login("bob2", "bobpass") != None

class UsersIntegrationTests:

    def test_create_user(self, app_context):
        # create a student record
        user = create_user("rick2@my.uwi.edu", "rick2", "bobpass")
        assert user.username == "rick2"

    def test_get_all_users_json(self, app_context):
        users_json = get_all_users_json()
        # returned data now includes email/role/points - just verify expected students present
        usernames = sorted([u.get('username') for u in users_json])
        self.assertIn('bob2', usernames)
        self.assertIn('rick2', usernames)

    # Tests data changes in the database
    def test_update_user(self, app_context):
        user = create_user("temp@my.uwi.edu", "temp", "pass")
        update_user(user.id, "ronnie")
        user = get_user(user.id)
        assert user.username == "ronnie"
        

