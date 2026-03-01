from .user import create_user
from .badge import createBadge
from App.database import db


def initialize():
    db.drop_all()
    db.create_all()

    # Create users
    bob = create_user('bob@my.uwi.edu', 'bob', 'bobpass')
    jane = create_user('jane@sta.uwi.edu', 'jane', 'janepass')

    # Create badges
    badge_25 = createBadge('25 Points', 'Awarded for earning 25 points', 25)
    badge_50 = createBadge('50 Points', 'Awarded for earning 50 points', 50)
    badge_75 = createBadge('75 Points', 'Awarded for earning 75 points', 75)

    # Create rewards
    from App.controllers.rewards import create_reward, redeem_reward
    reward_1 = create_reward('Free Coffee', 'Get a free coffee at the cafe', 10)
    reward_2 = create_reward('Book Voucher', 'Voucher for the bookstore', 30)

    # Create events
    from App.controllers.event import create_event, join_event, log_attendance
    from datetime import datetime, timedelta
    now = datetime.now()
    event1 = create_event(jane.id, 'Orientation', 'Seminar', 'Welcome event for new students', now - timedelta(days=10), now - timedelta(days=10, hours=-2))
    event2 = create_event(jane.id, 'Hackathon', 'Competition', 'Coding competition', now - timedelta(days=5), now - timedelta(days=5, hours=-4))
    event3 = create_event(jane.id, 'Workshop', 'Workshop', 'Python workshop', now - timedelta(days=2), now - timedelta(days=2, hours=-3))

    # Give Bob some points for demo
    from App.models import Student
    bob_obj = Student.query.filter_by(username='bob').first()
    if bob_obj:
        bob_obj.add_points(80)  # Give enough points for all badges and rewards
        db.session.commit()

        # Award badges to Bob
        from App.controllers.badge import awardBadge
        for badge in [badge_25, badge_50, badge_75]:
            if badge:
                awardBadge(bob_obj.id, badge.id)

        # Join Bob to events and log attendance
        for event in [event1, event2, event3]:
            event_id = event['id'] if event and isinstance(event, dict) and 'id' in event else None
            if event_id:
                join_event(bob_obj.id, event_id)
                log_attendance(bob_obj.id, event_id)

        # Redeem rewards for Bob
        for reward in [reward_1, reward_2]:
            if reward:
                redeem_reward(bob_obj.id, reward.id)
        db.session.commit()
    
