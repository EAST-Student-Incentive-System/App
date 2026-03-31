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
        create_db()

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
        create_db()

    def tearDown(self):
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


'''
    Integration Tests
'''

