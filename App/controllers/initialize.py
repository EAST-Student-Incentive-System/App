from time import sleep, time

from .user import create_user
from .badge import awardTestBadge, createBadge
from App.database import db
import random

def initialize():
    db.drop_all()
    db.create_all()

    # Create users
    bob = create_user('bob@my.uwi.edu', 'bob', 'bobpass')
    jane = create_user('jane@sta.uwi.edu', 'jane', 'janepass')
    print (f'Created users: {bob}, {jane}')

    # Create badges
    badge_25 = createBadge('25 Points', 'Awarded for earning 25 points', 25)
    badge_50 = createBadge('50 Points', 'Awarded for earning 50 points', 50)
    badge_75 = createBadge('75 Points', 'Awarded for earning 75 points', 75)
    badge_100 = createBadge('100 Points', 'Awarded for earning 100 points', 100)
    badge_Clean_Campus = createBadge('Clean Campus', 'Awarded for participating in a campus cleanup event', 20)
    badge_Community_Service = createBadge('Community Service', 'Awarded for volunteering in community service activities', 30)
    badge_Volunteer = createBadge('Volunteer', 'Awarded for volunteering at least 10 hours in any event', 40)
    badge_Event_Participant = createBadge('Event Participant', 'Awarded for attending at least 5 events', 50)
    badge_Helping_Hand = createBadge('Helping Hand', 'Awarded for assisting in organizing an event', 60)
    badge_Leadership = createBadge('Leadership', 'Awarded for leading an event or initiative', 80)
    badge_Savior_of_the_Planet = createBadge('Savior of the Planet', 'Awarded for participating in an environmental sustainability event', 100)
    badge_Health_and_Wellness = createBadge('Health and Wellness', 'Awarded for participating in a health and wellness event', 20)
    badge_Knight_of_Knowledge = createBadge('Knight of Knowledge', 'Awarded for attending a seminar or workshop', 30)
    badge_Cultural_Explorer = createBadge('Cultural Explorer', 'Awarded for attending a cultural event', 40)
    badge_Mage_of_Mentorship = createBadge('Mage of Mentorship', 'Awarded for mentoring another student', 50)
    badge_Social_Butterfly = createBadge('Social Butterfly', 'Awarded for attending a social event', 20)
    badge_Technology_Enthusiast = createBadge('Technology Enthusiast', 'Awarded for attending a technology-related event', 30)
    badge_Art_Aficionado = createBadge('Art Aficionado', 'Awarded for attending an art-related event', 30)
    badge_Sports_Fanatic = createBadge('Sports Fanatic', 'Awarded for attending a sports event', 20)
    badge_Thief_of_Time = createBadge('Thief of Time', 'Awarded for attending an event outside of regular hours', 40)
    badge_Night_Owl = createBadge('Night Owl', 'Awarded for attending an event that starts after 6 PM', 30)
    badge_Enemy_of_Boredom = createBadge('Enemy of Boredom', 'Awarded for attending an event on a weekend', 20)
    badge_Early_Bird = createBadge('Early Bird', 'Awarded for attending an event that starts before 9 AM', 30)
    badge_Distinguished_Services = createBadge('Distinguished Services', 'Awarded for exceptional contributions to the campus community', 100)
    badge_Community_Champion = createBadge('Community Champion', 'Awarded for outstanding involvement in community service', 80)
    badge_Heroism = createBadge('Heroism', 'Awarded for acts of bravery or heroism during campus events', 100)
    badge_Innovator = createBadge('Innovator', 'Awarded for introducing a new idea or initiative that benefits the campus community', 70)
    badge_Faker = createBadge('Faker', 'Awarded for attending an event without checking in (for testing purposes)', 0)
    badge_Jack_of_All_Trades = createBadge('Jack of All Trades', 'Awarded for attending events in at least 5 different categories', 50)
    

    # Create rewards
    from App.controllers.rewards import create_reward, redeem_reward
    reward_1 = create_reward('Free Coffee', 'Get a free coffee at the cafe', 10 ,2)
    reward_2 = create_reward('Book Voucher', 'Voucher for the bookstore', 30 ,2)
    reward_3 = create_reward('Event Swag', 'Exclusive swag from campus events', 50 ,2)
    reward_4 = create_reward('Priority Registration', 'Get priority registration for classes', 100 ,2)
    reward_5 = create_reward('VIP Event Access', 'Get VIP access to select campus events', 150 ,2)
    KFC_Bucket = create_reward('KFC Bucket', 'A bucket of KFC chicken', 20 ,2)
    Starbucks_Gift_Card = create_reward('Starbucks Gift Card', 'A $10 gift card for Starbucks', 25 ,2)
    Movie_Tickets = create_reward('Movie Tickets', 'Two tickets to the movies', 30 ,2)
    Massage_Coupon = create_reward('Massage Coupon', 'A coupon for a free massage at the campus wellness center', 40 ,2)
    Dorm_Snack_Box = create_reward('Dorm Snack Box', 'A box of snacks delivered to your dorm room', 15 ,2)
    #//Fake_Reward = create_reward('Fake Reward', 'This reward is for testing purposes and has no point cost', 0 ,2)

    # Create events
    from App.controllers.event import create_event, join_event, log_attendance
    from datetime import datetime, timedelta
    now = datetime.now()
    event1 = create_event(jane.id, 'Orientation', 'Seminar', 'Welcome event for new students', now - timedelta(days=10), now - timedelta(days=10, hours=-2), 'Campus Hall', None, True)
    event2 = create_event(jane.id, 'Hackathon', 'Competition', 'Coding competition', now - timedelta(days=5), now - timedelta(days=5, hours=-4), 'Tech Lab', None, True)
    event3 = create_event(jane.id, 'Workshop', 'Workshop', 'Python workshop', now - timedelta(days=2), now - timedelta(days=2, hours=-3), 'Lecture Room 101', None, True)
    event4 = create_event(jane.id, 'Community Service', 'Volunteer', 'Beach cleanup event', now + timedelta(days=3), now + timedelta(days=3, hours=2), 'Beach', None, True)
    event5 = create_event(jane.id, 'Health Fair', 'Health', 'Campus health fair with free screenings and wellness resources', now + timedelta(days=7), now + timedelta(days=7, hours=4), 'Student Center', None, True)
    event6 = create_event(jane.id, 'Cultural Festival', 'Cultural', 'Celebration of diverse cultures with food, music, and performances', now + timedelta(days=14), now + timedelta(days=14, hours=5), 'Main Quad', None, True)
    event7 = create_event(jane.id, 'Tech Talk', 'Seminar', 'Guest speaker discussing emerging technologies', now + timedelta(days=21), now + timedelta(days=21, hours=2), 'Tech Auditorium', None, True)
    event8 = create_event(jane.id, 'Art Exhibition', 'Art', 'Showcase of student artwork', now + timedelta(days=28), now + timedelta(days=28, hours=3), 'Art Gallery', None, True)
    event9 = create_event(jane.id, 'Sports Tournament', 'Sports', 'Intramural sports tournament', now + timedelta(days=35), now + timedelta(days=35, hours=6), 'Sports Complex', None, True)
    event10 = create_event(jane.id, 'Environmental Summit', 'Environment', 'Panel discussion on sustainability initiatives', now + timedelta(days=42), now + timedelta(days=42, hours=4), 'Conference Center', None, True)

    # Give Bob some points for demo
    from App.models import Student
    bob_obj = Student.query.filter_by(username='bob').first()
    if bob_obj:
        bob_obj.add_points(999)  # Give enough points for all badges and rewards
        db.session.commit()

        # Award ALL badges to Bob
        from App.controllers.badge import awardBadge
        for badge in [badge_25, badge_50, badge_75, badge_100, badge_Clean_Campus, badge_Community_Service, badge_Volunteer, badge_Event_Participant, badge_Helping_Hand, badge_Leadership, badge_Savior_of_the_Planet, badge_Health_and_Wellness, badge_Knight_of_Knowledge, badge_Cultural_Explorer, badge_Mage_of_Mentorship, badge_Social_Butterfly, badge_Technology_Enthusiast, badge_Art_Aficionado, badge_Sports_Fanatic, badge_Thief_of_Time, badge_Night_Owl, badge_Enemy_of_Boredom, badge_Early_Bird, badge_Distinguished_Services, badge_Community_Champion, badge_Heroism, badge_Innovator, badge_Faker, badge_Jack_of_All_Trades]:
            if badge:
                awardTestBadge(bob_obj.id, badge.id, datetime.now()+timedelta(days=random.randint(1, 30)))  # Use the test badge awarding function to set earned_at at a random time. This will help demonstrate the student history page with badges earned at different times. Should be removed or modified for production use.
            else:
                print(f'Failed to create badge: {badge}')
        print(f'Bob has been awarded badges: {[badge.name for badge in [badge_25, badge_50, badge_75] if badge]}')
        
        # Join Bob to ALL events and log attendance
        print("Now attempting to join events and log attendance for Bob...")
        for event in [event1, event2, event3, event4, event5, event6, event7, event8, event9, event10]:
            if event and hasattr(event, 'id') and hasattr(event, 'name'):
                join_event(bob_obj.id, event.id)
                log_attendance(bob_obj.id, event.id, datetime.now() + timedelta(days=random.randint(1, 300)))  # Log attendance with a random timestamp to demonstrate the student history page. Should be removed or modified for production use.
                print(f'Bob attended event: {event.id} - {event.name}')
            else:
                print(f'Failed to create event: {event}')
        # Redeem ALL rewards for Bob
        for reward in [reward_1, reward_2, reward_3, reward_4, reward_5, KFC_Bucket, Starbucks_Gift_Card, Movie_Tickets, Massage_Coupon, Dorm_Snack_Box]:
            if reward:
                redeem_reward(bob_obj.id, reward.id, datetime.now() + timedelta(days=random.randint(1, 300)))  # Redeem with a random timestamp to demonstrate the student history page. Should be removed or modified for production use.
                print(f'Bob redeemed reward: {reward.name} for {reward.pointCost} points')
            else:
                print(f'Failed to create reward: {reward}')
        db.session.commit()
    else:
        print('Failed to create user Bob. Please check the user creation process.')
