import re
import os, tempfile, pytest, logging, unittest
#from turtle import st
from werkzeug.security import check_password_hash, generate_password_hash
import base64
import time
from flask_jwt_extended import create_access_token, verify_jwt_in_request
from App.controllers.badge import awardEventTypeBadge
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
    log_attendance, generate_qr, get_participant_count, signUp, change_password,
    createBadge, awardBadge, student_has_badge, check_and_award_badges, viewBadges, viewStudentBadges
)
from App.controllers.rewards import (
    create_reward, 
    get_reward, get_all_rewards, get_all_rewards_json, get_active_rewards, 
    update_reward, toggle_reward, redeem_reward, viewReward, viewRewardHistory
)
from App.models import student, RedeemedReward
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
        

class RewardUnitTests(unittest.TestCase):
    def setUp(self):
        # fresh test app + db (match your existing tests)
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///test.db"})
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.rollback()
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_isRedeemable_inactive_false(self):
        r = Reward(name="Coffee", description="Hot drink", pointCost=50, active=False)
        self.assertFalse(r.isRedeemable(999))

    def test_isRedeemable_not_enough_points_false(self):
        r = Reward(name="Coffee", description="Hot drink", pointCost=50, active=True)
        self.assertFalse(r.isRedeemable(49))

    def test_isRedeemable_exact_points_true(self):
        r = Reward(name="Coffee", description="Hot drink", pointCost=50, active=True)
        self.assertTrue(r.isRedeemable(50))

    def test_get_json_fields(self):
        r = Reward(
            name="Coffee",
            description="Hot drink",
            pointCost=50,
            active=True,
            created_by=123,
            image="http://example.com/image.png",
            limit=10,
        )
        db.session.add(r)
        db.session.commit()

        data = r.get_json()
        self.assertEqual(data["id"], r.id)
        self.assertEqual(data["name"], "Coffee")
        self.assertEqual(data["description"], "Hot drink")
        self.assertEqual(data["pointCost"], 50)
        self.assertEqual(data["active"], True)
        self.assertEqual(data["createdBy"], 123)
        self.assertEqual(data["image"], "http://example.com/image.png")
        self.assertEqual(data["limit"], 10)


    def test_toggle_flips_active_and_persists(self):
        r = Reward(name="Coffee", description="Hot drink", pointCost=50, active=True)
        db.session.add(r)
        db.session.commit()

        rid = r.id
        self.assertTrue(r.active)

        # act
        r.toggle()

        # reload from DB to ensure it persisted
        refreshed = db.session.get(Reward, rid)
        self.assertIsNotNone(refreshed)
        self.assertFalse(refreshed.active)

        # toggle back
        refreshed.toggle()
        refreshed2 = db.session.get(Reward, rid)
        self.assertTrue(refreshed2.active)

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

class BadgeIntegrationTests(unittest.TestCase):

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

    def test_student_has_badge_true(self):
        student1 = create_user("student1@my.uwi.edu", "student1", "pass")
        badge1 = createBadge("Badge1", "Desc", 0, "milestone")
        awarded = awardBadge(student1.id, badge1.id)
        has_badge = student_has_badge(student1.id, badge1.id)
        assert has_badge is True

    def test_student_has_badge_false(self):
        student2 = create_user("student2@my.uwi.edu", "student2", "pass")
        badge2 = createBadge("Badge2", "Desc", 0, "milestone")
        has_badge = student_has_badge(student2.id, badge2.id)
        assert has_badge is False

    def test_awardBadge_event_type_badge(self):
        student3 = create_user("student3@my.uwi.edu", "student3", "pass")
        badge3 = createBadge("Badge3", "Desc", 0, "event_type")
        awarded = awardBadge(student3.id, badge3.id)
        assert awarded is False

    def test_awardBadge_sufficient_points(self):
        student4 = create_user("student4@my.uwi.edu", "student4", "pass")
        badge4 = createBadge("Badge4", "Desc", 50, "milestone")
        student4.add_points(100)
        awarded = awardBadge(student4.id, badge4.id)
        assert awarded is True

    def test_awardBadge_insufficient_points(self):
        student5 = create_user("student5@my.uwi.edu", "student5", "pass")
        badge5 = createBadge("Badge5", "Desc", 50, "milestone")
        awarded = awardBadge(student5.id, badge5.id)
        assert awarded is False

    def test_awardBadge_already_earned(self):
        student6 = create_user("student6@my.uwi.edu", "student6", "pass")
        badge6 = createBadge("Badge6", "Desc", 50, "milestone")
        student6.add_points(100)
        awarded = awardBadge(student6.id, badge6.id)
        award_again = awardBadge(student6.id, badge6.id)
        assert award_again is False

    def test_awardEventTypeBadge_non_event_type(self):
        student7 = create_user("student7@my.uwi.edu", "student7", "pass")
        badge7 = createBadge("Badge7", "Desc", 0, "milestone")
        awarded = awardEventTypeBadge(student7.id, badge7.id)
        assert awarded is False

    def test_awardEventTypeBadge_success(self):
        student8 = create_user("student8@my.uwi.edu", "student8", "pass")
        badge8 = createBadge("Attended Workshop", "Desc", 0, "event_type")
        awarded = awardEventTypeBadge(student8.id, badge8.id)
        assert awarded is True

    def test_awardEventTypeBadge_already_earned(self):
        student9 = create_user("student9@my.uwi.edu", "student9", "pass")
        badge9 = createBadge("Attended Seminar", "Desc", 0, "event_type")
        awarded = awardEventTypeBadge(student9.id, badge9.id)
        award_again = awardEventTypeBadge(student9.id, badge9.id)
        assert award_again is False

    def test_check_and_award_badges(self):
        staff1 = create_user("staff1@sta.uwi.edu", "staff1", "pass")
        event = create_event(
            staff_id=staff1.id, name="Test Event", type="Lecture", description="Desc",
            start=datetime.now() - timedelta(hours=1), end=datetime.now() + timedelta(hours=1),
            location="Room", image=None, active=True
        )
        student10 = create_user("student10@my.uwi.edu", "student10", "pass")
        badge10 = createBadge("Milestone Badge", "Desc", 50, "milestone")
        badge11 = createBadge("Attended Lecture", "Desc", 0, "event_type")
        student10.add_points(100)
        check_and_award_badges(student10, event)
        assert student_has_badge(student10.id, badge10.id) is True
        assert student_has_badge(student10.id, badge11.id) is True

    def test_viewBadges(self):
        badge12 = createBadge("Badge12", "Desc", 0, "milestone")
        badge13 = createBadge("Badge13", "Desc", 0, "milestone")
        badges = viewBadges()
        assert badge12 in badges
        assert badge13 in badges

    def test_viewStudentBadges(self):
        student11 = create_user("student11@my.uwi.edu", "student11", "pass")
        badge14 = createBadge("Badge14", "Desc", 0, "milestone")
        awardBadge(student11.id, badge14.id)   
        student_badges = viewStudentBadges(student11.id)
        assert len(student_badges) == 1
        assert student_badges[0].badge_id == badge14.id


class TestRewardsIntegration(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///test.db",
            # If your app doesn't already set this in create_app, you may need it:
            # "JWT_SECRET_KEY": "test-secret",
        })
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        self.staff = create_user("rewardstaff@sta.uwi.edu", "rewardstaff", "pass123")
        self.student = create_user("rewardstudent@my.uwi.edu", "rewardstudent", "pass123")

        # JWT identity used by get_jwt_identity()
        self.staff_token = create_access_token(identity=self.staff.id)
        self.staff_headers = {"Authorization": f"Bearer {self.staff_token}"}

        self.student.current_balance = 200
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    # -------------------------------------------------------------------------
    # test_create_reward()
    # Ensures reward record is created with correct name, description, point cost and active values
    def test_create_reward(self):
        r = create_reward(
            name="Coffee",
            description="Hot drink",
            point_cost=50,
            created_by=self.staff.id,
            active=True,
            image=None,
            limit=None,
        )
        self.assertIsNotNone(r)
        self.assertEqual(r.name, "Coffee")
        self.assertEqual(r.description, "Hot drink")
        self.assertEqual(r.pointCost, 50)
        self.assertTrue(r.active)

        fetched = get_reward(r.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.name, "Coffee")
        self.assertEqual(fetched.description, "Hot drink")
        self.assertEqual(fetched.pointCost, 50)
        self.assertTrue(fetched.active)

    # -------------------------------------------------------------------------
    # test_get_all_rewards()
    # Verifies that all rewards in the system can be retrieved
    def test_get_all_rewards(self):
        create_reward("A", "desc", 10, self.staff.id, active=True, image=None, limit=None)
        create_reward("B", "desc", 20, self.staff.id, active=False, image=None, limit=None)

        rewards = get_all_rewards()
        self.assertIsInstance(rewards, list)
        self.assertEqual(len(rewards), 2)

    # -------------------------------------------------------------------------
    # test_get_all_rewards_json()
    # Verifies json data of all rewards in the system
    def test_get_all_rewards_json(self):
        create_reward("A", "desc", 10, self.staff.id, active=True, image=None, limit=None)
        create_reward("B", "desc", 20, self.staff.id, active=False, image=None, limit=None)

        rewards = get_all_rewards()
        self.assertEqual(len(rewards), 2)

        rewards_json = get_all_rewards_json()
        self.assertIsInstance(rewards_json, list)
        self.assertEqual(len(rewards_json), 2)

        # Key names depend on your Reward.get_json(); these are common with your codebase
        self.assertIn("name", rewards_json[0])
        self.assertIn("description", rewards_json[0])
        self.assertIn("pointCost", rewards_json[0])
        self.assertIn("active", rewards_json[0])

    # -------------------------------------------------------------------------
    # test_get_active_rewards()
    # Ensures only active rewards are returned
    def test_get_active_rewards(self):
        create_reward("Active1", "desc", 10, self.staff.id, active=True, image=None, limit=None)
        create_reward("Inactive1", "desc", 20, self.staff.id, active=False, image=None, limit=None)

        active = get_active_rewards()
        self.assertIsInstance(active, list)
        self.assertTrue(all(r.active for r in active))
        names = [r.name for r in active]
        self.assertIn("Active1", names)
        self.assertNotIn("Inactive1", names)

    # -------------------------------------------------------------------------
    # test_update_reward()
    # Verifies that the correct fields are updated with the correct values
    def test_update_reward(self):
        r = create_reward("Old", "old desc", 10, self.staff.id, active=True, image=None, limit=None)

        updated = update_reward(
            r.id,
            created_by=self.staff.id,   # role check (staff) in your controller
            name="New",
            description="new desc",
            point_cost=99,
            active=False,
        )
        self.assertIsNotNone(updated)

        fetched = get_reward(r.id)
        self.assertEqual(fetched.name, "New")
        self.assertEqual(fetched.description, "new desc")
        self.assertEqual(fetched.pointCost, 99)
        self.assertFalse(fetched.active)

    # -------------------------------------------------------------------------
    # test_toggle_reward()
    # Verifies reward active state toggles between True and False
    def test_toggle_reward(self):
        r = create_reward("ToggleMe", "desc", 10, self.staff.id, active=True, image=None, limit=None)

        with self.app.test_request_context(headers=self.staff_headers):
            verify_jwt_in_request()
            toggle_reward(r.id)

        fetched1 = get_reward(r.id)
        self.assertFalse(fetched1.active)

        with self.app.test_request_context(headers=self.staff_headers):
            verify_jwt_in_request()
        toggle_reward(r.id)

        fetched2 = get_reward(r.id)
        self.assertTrue(fetched2.active)
    # -------------------------------------------------------------------------
    # test_redeem_reward()
    # Verifies a student can redeem a reward when having a sufficient balance of points
    # and a RedeemedReward record is created
    def test_redeem_reward(self):
        r = create_reward("Coffee", "desc", 50, self.staff.id, active=True, image=None, limit=None)

        before = self.student.current_balance

        result = redeem_reward(self.student.id, r.id)
        
        self.assertTrue(result is not False)

        db.session.refresh(self.student)
        self.assertEqual(self.student.current_balance, before - r.pointCost)

        rr = RedeemedReward.query.filter_by(student_id=self.student.id, reward_id=r.id).first()
        self.assertIsNotNone(rr)

        # optional: reward limit/stock handling could change pointCost etc; we just ensure reward still exists
        fetched_reward = get_reward(r.id)
        self.assertIsNotNone(fetched_reward)

    # -------------------------------------------------------------------------
    # test_redeem_reward_insufficient_balance()
    # Ensures False is returned when a student lacks sufficient points to redeem a reward
    def test_redeem_reward_insufficient_balance(self):
        r = create_reward("Coffee", "desc", 500, self.staff.id, active=True, image=None, limit=None)

        self.student.current_balance = 10
        db.session.commit()

        result = redeem_reward(self.student.id, r.id)
        self.assertFalse(result)

        rr = RedeemedReward.query.filter_by(student_id=self.student.id, reward_id=r.id).first()
        self.assertIsNone(rr)

    # -------------------------------------------------------------------------
    # test_redeem_reward_inactive()
    # Verifies inactive rewards cannot be redeemed
    def test_redeem_reward_inactive(self):
        r = create_reward("Coffee", "desc", 50, self.staff.id, active=True, image=None, limit=None)

        with self.app.test_request_context(headers=self.staff_headers):
            verify_jwt_in_request()
            toggle_reward(r.id)  # now inactive

        fetched = get_reward(r.id)
        self.assertFalse(fetched.active)

        result = redeem_reward(self.student.id, r.id)
        self.assertFalse(result)

        rr = RedeemedReward.query.filter_by(student_id=self.student.id, reward_id=r.id).first()
        self.assertIsNone(rr)

    # -------------------------------------------------------------------------
    # test_viewReward()
    # Ensures all active and redeemable rewards are returned
    def test_viewReward(self):
        # Student balance 200 from setUp
        create_reward("Cheap", "desc", 50, self.staff.id, active=True, image=None, limit=None)     # redeemable
        create_reward("Expensive", "desc", 500, self.staff.id, active=True, image=None, limit=None)  # not redeemable
        create_reward("Inactive", "desc", 10, self.staff.id, active=False, image=None, limit=None)

        rewards = viewReward(self.student.id)
        self.assertIsInstance(rewards, list)

        names = [r.name for r in rewards]
        self.assertIn("Cheap", names)
        self.assertIn("Expensive", names)
        self.assertNotIn("Inactive", names)  # only active rewards should appear

        # If your viewReward sets a dynamic attribute `redeemable`, validate it
        by_name = {r.name: r for r in rewards}
        self.assertTrue(hasattr(by_name["Cheap"], "redeemable"))
        self.assertTrue(by_name["Cheap"].redeemable)
        self.assertFalse(by_name["Expensive"].redeemable)

    # -------------------------------------------------------------------------
    # test_viewRewardHistory()
    # Verifies all rewards created by a specific staff member are returned
    def test_viewRewardHistory(self):
        staff2 = create_user("rewardstaff2@sta.uwi.edu", "rewardstaff2", "pass123")

        create_reward("S1", "desc", 10, self.staff.id, active=True, image=None, limit=None)
        create_reward("S2", "desc", 20, self.staff.id, active=True, image=None, limit=None)
        create_reward("OtherStaff", "desc", 30, staff2.id, active=True, image=None, limit=None)

        hist = viewRewardHistory(self.staff.id)
        self.assertIsInstance(hist, list)

    # viewRewardHistory returns list of dicts (Reward.get_json())
        hist_names = [r.get("name") for r in hist]

        self.assertIn("S1", hist_names)
        self.assertIn("S2", hist_names)
        self.assertNotIn("OtherStaff", hist_names)