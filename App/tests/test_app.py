import re
import os, tempfile, pytest, logging, unittest
from turtle import st
from werkzeug.security import check_password_hash, generate_password_hash
import base64
import time
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
    get_student_history, create_event, update_event, delete_event,
    get_event, view_upcoming_events, view_all_events,
    view_event_history, join_event, leave_event,
    log_attendance, generate_qr, get_participant_count, signUp, change_password
)
from App.models import student
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
from App.models import Student, Event, Attendance, Badge

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

class BadgeUnitTests(unittest.TestCase):

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

    def test_meets_requirements_event(self):
        badge = Badge(name="Event Badge", type="event_type", points_required=0)
        student = Student(email="bob@test.com", username="bob", password="pw")
        student.points = 999  # even with plenty of points, should still be False
        db.session.add_all([badge, student])
        db.session.commit()
        self.assertFalse(badge.meets_requirements(student))

    def test_meets_requirements_milestone(self):
        badge = Badge(name="Milestone Badge", type="milestone", points_required=50)
        student_pass = Student(email="pass@test.com", username="passing", password="pw")
        student_fail = Student(email="fail@test.com", username="failing", password="pw")
        student_pass.points = 50   # exactly at threshold — should pass
        student_fail.points = 49   # one below threshold — should fail
        db.session.add_all([badge, student_pass, student_fail])
        db.session.commit()
        self.assertTrue(badge.meets_requirements(student_pass))
        self.assertFalse(badge.meets_requirements(student_fail))
        

'''
    Integration Tests
'''
@pytest.fixture
def app():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def app_context(app):
        yield

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

class UsersIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        # seed the user that other tests depend on
        create_user("bob2@my.uwi.edu", "bob2", "bobpass")

    def tearDown(self):
        db.session.rollback()
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_create_user(self):
        # create a student record
        user = create_user("rick2@my.uwi.edu", "rick2", "bobpass")
        assert user.username == "rick2"

    def test_get_all_users_json(self):
        create_user("rick2@my.uwi.edu", "rick2", "bobpass")
        users_json = get_all_users_json()
        # returned data now includes email/role/points - just verify expected students present
        usernames = sorted([u.get('username') for u in users_json])
        self.assertIn('bob2', usernames)
        self.assertIn('rick2', usernames)

    # Tests data changes in the database
    def test_update_user(self):
        user = create_user("temp@my.uwi.edu", "temp", "pass")
        update_user(user.id, "ronnie")
        user = get_user(user.id)
        assert user.username == "ronnie"


class TestEventIntegrationTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Create some common users
        self.staff = create_user("staff@sta.uwi.edu", "staff1", "pass")
        self.student = create_user("student@my.uwi.edu", "student1", "pass")

        # Create a default event
        self.event = create_event(
            staff_id=self.staff.id,
            name="Test Event",
            type="Workshop",
            description="Desc",
            start=datetime.now() + timedelta(hours=1),
            end=datetime.now() + timedelta(hours=2),
            location="Room 1",
            image=None,
            active=True,
            limit=10
        )

    def tearDown(self):
        db.session.rollback()
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_create_event(self):
        event = create_event(
            self.staff.id, "Event", "Type", "Desc",
            datetime.now(), datetime.now() + timedelta(hours=1),
            "Room", None, True
        )

        assert event is not None
        assert event.name == "Event"
        assert event.staffId == self.staff.id

    def test_update_event(self):
        updated = update_event(
            self.event.id,
            staff_id=self.staff.id,
            name="Updated Name"
        )

        assert updated is not None
        assert updated["name"] == "Updated Name"

    def test_delete_event_success(self):
        result = delete_event(self.event.id, self.staff.id)
        assert result is True
        assert get_event(self.event.id) is None
    
    def test_view_upcoming_events(self):
        past = create_event(
            self.staff.id, "Past", "Type", "Desc",
            datetime.now() - timedelta(days=1),
            datetime.now(),
            "Room", None, True
        )

        future = create_event(
            self.staff.id, "Future", "Type", "Desc",
            datetime.now() + timedelta(days=1),
            datetime.now() + timedelta(days=2),
            "Room", None, True
        )

        events = view_upcoming_events()
        assert future in events
        assert past not in events


    def test_view_all_events(self):
        events = view_all_events()
        assert len(events) > 0

    def test_view_event_history_staff(self):
        e1 = create_event(self.staff.id, "E1", "T", "D",
                        datetime.now(), datetime.now(), "R", None, True)
        e2 = create_event(self.staff.id, "E2", "T", "D",
                        datetime.now(), datetime.now(), "R", None, True)

        history = view_event_history(staff_id=self.staff.id)

        assert e1 in history
        assert e2 in history

    def test_view_event_history_student(self):
        join_event(self.student.id, self.event.id)

        self.event.start = datetime.now() - timedelta(hours=1)
        db.session.commit()

        log_attendance(self.student.id, self.event.id)

        history = view_event_history(student_id=self.student.id)

        assert len(history) == 1

    def test_join_event(self):
        result = join_event(self.student.id, self.event.id)
        assert result is True
        assert self.student in self.event.students

    def test_join_event_already_joined(self):
        join_event(self.student.id, self.event.id)
        result = join_event(self.student.id, self.event.id)
        assert result is False

    def test_join_event_full(self):
        event = create_event(
            self.staff.id, "Limited", "T", "D",
            datetime.now(), datetime.now(),
            "Room", None, True, limit=1
        )

        s1 = create_user("s1@my.uwi.edu", "s1", "pass")
        s2 = create_user("s2@my.uwi.edu", "s2", "pass")

        join_event(s1.id, event.id)
        result = join_event(s2.id, event.id)

        assert result is False

    def test_leave_event(self):
        join_event(self.student.id, self.event.id)
        leave_event(self.student.id, self.event.id)

        assert self.student not in self.event.students

    def test_log_attendance(self):
        join_event(self.student.id, self.event.id)

        self.event.start = datetime.now() - timedelta(minutes=10)
        db.session.commit()

        result = log_attendance(self.student.id, self.event.id)

        assert result is not None

    def test_log_attendance_not_joined(self):
        result = log_attendance(self.student.id, self.event.id)
        assert result is False

    def test_log_attendance_outside_timeframe(self):
        join_event(self.student.id, self.event.id)

        result = log_attendance(self.student.id, self.event.id)
        assert result is False

    def test_log_attendance_duplicate(self):
        join_event(self.student.id, self.event.id)

        self.event.start = datetime.now() - timedelta(minutes=10)
        db.session.commit()

        log_attendance(self.student.id, self.event.id)
        result = log_attendance(self.student.id, self.event.id)

        assert result is False

    def test_generate_qr_code(self):
        qr = generate_qr(self.event.id)

        assert isinstance(qr, str)

        decoded = base64.b64decode(qr)
        assert decoded is not None

    def test_get_participant_count(self):
        join_event(self.student.id, self.event.id)

        count = get_participant_count(self.event.id)
        assert count == 1

    def test_get_participant_count_with_cutoff(self):
        join_event(self.student.id, self.event.id)

        cutoff = datetime.now() + timedelta(minutes=1)
        count = get_participant_count(self.event.id, cutoff=cutoff)

        assert count == 1

class AuthenticationIntegrationTests(unittest.TestCase):

    def setUp(self):
        # fresh test app + db
        self.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.rollback()
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_signUp_student(self):
        result = signUp("student1@my.uwi.edu", "student1", "pass123")
        assert result.get("success") is True
        assert result["user"]["role"] == "student"

    def test_signUp_staff(self):
        result = signUp("staff1@sta.uwi.edu", "staff1", "pass123")
        assert result.get("success") is True
        assert result["user"]["role"] == "staff"

    def test_signUp_duplicate_email(self):
        signUp("dup@my.uwi.edu", "dupuser", "pass123")
        result = signUp("dup@my.uwi.edu", "anotheruser", "pass123")
        assert "error" in result
        assert result["error"] == "Email already registered."

    def test_signUp_duplicate_username(self):
        signUp("unique@my.uwi.edu", "dupuser", "pass123")
        result = signUp("another@my.uwi.edu", "dupuser", "pass123")
        assert "error" in result
        assert result["error"] == "Username already taken."

    def test_login_success(self):
        signUp("login@my.uwi.edu", "loginuser", "pass123")
        result = login("loginuser", "pass123", device_id="DEVICE1")
        assert "access_token" in result
        assert result["user"]["username"] == "loginuser"
        assert result["role"] == "student"

    def test_login_failure(self):
        signUp("fail@my.uwi.edu", "failuser", "pass123")
        result = login("failuser", "wrongpass")
        assert "error" in result
        assert result["error"] == "Invalid username or password."

    def test_change_password(self):
        signUp("changepw@my.uwi.edu", "changepwuser", "oldpass")
        result = change_password("changepw@my.uwi.edu", "oldpass", "newpass")
        assert result.get("success") is True
        # verify login works with new password
        login_result = login("changepwuser", "newpass")
        assert "access_token" in login_result

    def test_change_password_old_invalid(self):
        signUp("wrongold@my.uwi.edu", "wrongolduser", "oldpass")
        result = change_password("wrongold@my.uwi.edu", "badold", "newpass")
        assert "error" in result
        assert result["error"] == "Invalid email or old password."
