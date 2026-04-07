from time import sleep, time

from .user import create_user
from .badge import createBadge
from App.database import db
from App.models import Student, Staff
import random

def initialize():
    db.drop_all()
    db.create_all()

    # Create users
    bob = create_user('bob@my.uwi.edu', 'bob', 'bobpass')
    jane = create_user('jane@sta.uwi.edu', 'jane', 'janepass')
    alice = create_user('alice@my.uwi.edu', 'alice', 'alicepass')
    print (f'Created users: {bob}, {jane}, {alice}')

    bob_obj = Student.query.filter_by(username='bob').first()
    alice_obj = Student.query.filter_by(username='alice').first()
    jane_obj = Staff.query.filter_by(username='jane').first()

    if bob_obj and alice_obj:
        bob_obj.temporary_device_holder = "DEVICE123"
        alice_obj.temporary_device_holder = "DEVICE123"
        bob_obj.is_verified = True  # Mark Bob as verified for testing purposes
        alice_obj.is_verified = True  # Mark Alice as verified for testing purposes
        db.session.commit()

    if jane_obj:
        jane_obj.is_verified = True  # Mark Jane as verified for testing purposes
        db.session.commit()

    # Create badges
    badge_25 = createBadge('25 Points', 'Awarded for earning 25 points', 25 , 'milestone')
    badge_50 = createBadge('50 Points', 'Awarded for earning 50 points', 50 , 'milestone')
    badge_75 = createBadge('75 Points', 'Awarded for earning 75 points', 75, 'milestone')
    badge_100 = createBadge('100 Points', 'Awarded for earning 100 points', 100, 'milestone')
    badge_Community_Service = createBadge('Community Service', 'Awarded for volunteering in community service activities', None, 'Volunteer')
    badge_Knight_of_Knowledge = createBadge('Knight of Knowledge', 'Awarded for attending a seminar', None, 'Seminar')
    badge_Cultural_Explorer = createBadge('Explorer', 'Awarded for attending a Workshop event', None, 'Workshop')
    badge_Social_Butterfly = createBadge('Social Butterfly', 'Awarded for attending a social event', None, 'Social')
    badge_Thief_of_Time = createBadge('Thief of Time', 'Awarded for attending 200 hours of events', 200, 'milestone')
    badge_Night_Owl = createBadge('Night Owl', 'Awarded for attending 250 hours of events', 250, 'milestone')
    badge_Enemy_of_Boredom = createBadge('Enemy of Boredom', 'Awarded for attending 300 hours of events', 300, 'milestone')
    badge_Distinguished_Services = createBadge('Distinguished Services', 'Awarded for exceptional contributions to the campus community for over 350 hours', 350, 'milestone')
    badge_Community_Champion = createBadge('Community Champion', 'Awarded for outstanding involvement in community service for over 400 hours', 400, 'milestone')
    badge_Sleep_Deprived = createBadge('Sleep Deprived', 'Awarded for attending 450 hours of events', 450, 'milestone')
    badge_Jack_of_All_Trades = createBadge('Jack of All Trades', 'Awarded for attending 500 hours of events', 500, 'milestone')
    badge_Globetrotter = createBadge('Globetrotter', 'Awarded for attending 1000 hours of events', 1000, 'milestone')
    badge_Master= createBadge('Master of Ceremonies', 'Awarded for attending 2000 hours of events', 2000, 'milestone')
    badge_Grand_Master = createBadge('Grand Master', 'Awarded for attending 3000 hours of events', 3000, 'milestone')
    badge_Immortal = createBadge('Immortal', 'Awarded for attending 4000 hours of events', 4000, 'milestone')
    badge_Legend = createBadge('Legend', 'Awarded for attending 5000 hours of events', 5000, 'milestone')
    badge_Rookie = createBadge('Rookie', 'Awarded for attending your first event', 1, 'milestone')
    badge_King_of_the_Campus = createBadge('King of the Campus', 'Awarded for attending 10000 hours of events', 10000, 'milestone')

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
    Ultimate_Pizza_Party = create_reward('Ultimate Pizza Party', 'A pizza party for you and 10 friends in the campus lounge', 2000 ,2)
    #//Fake_Reward = create_reward('Fake Reward', 'This reward is for testing purposes and has no point cost', 0 ,2)

    # Create events
    from App.controllers.event import create_event, join_event, log_attendance
    from datetime import datetime, timedelta
    now = datetime.now()

    def create_active_event(owner_id, name, type, desc, location):
        start = now - timedelta(hours=1)   # started 1 hour ago
        end   = now + timedelta(hours=1)   # ends 1 hour from now
        return create_event(owner_id, name, type, desc, start, end, location, None, True)

    event1 = create_active_event(jane.id, 'Orientation', 'Social', 'Welcome to campus! Join us for orientation activities and meet your fellow students.', 'Main Auditorium')
    event2 = create_active_event(jane.id, 'Tech Talk', 'Technology', 'Learn about the latest trends in technology with industry experts.', 'Engineering Building, Room 101')
    event3 = create_active_event(jane.id, 'Yoga Class', 'Health & Wellness', 'Relax and unwind with a yoga session led by a certified instructor.', 'Campus Gym')
    event4 = create_active_event(jane.id, 'Cultural Festival', 'Cultural', 'Experience the rich diversity of our campus with food, music, and performances from around the world.', 'Student Center Lawn')
    event5 = create_active_event(jane.id, 'Career Fair', 'Career', 'Connect with potential employers and learn about internship and job opportunities.', 'Exhibition Hall')
    event6 = create_active_event(jane.id, 'Art Workshop', 'Art', 'Get creative with a hands-on art workshop led by local artists.', 'Art Building, Room 202')
    event7 = create_active_event(jane.id, 'Environmental Cleanup', 'Community Service', 'Join us for a campus cleanup event and earn points while making a positive impact on the environment.', 'Meet at Campus Entrance')
    event8 = create_active_event(jane.id, 'Cooking Class', 'Food', 'Learn to cook a new dish with a cooking class led by a local chef.', 'Culinary Arts Building, Room 303')
    event9 = create_active_event(jane.id, 'Dance Party', 'Social', 'Dance the night away at our campus dance party with a live DJ and refreshments.', 'Student Center Ballroom')
    event10 = create_active_event(jane.id, 'Sports Tournament', 'Sports', 'Compete in a friendly sports tournament with your fellow students. All skill levels welcome!', 'Campus Sports Field')
    event11 = create_active_event(jane.id, 'Movie Night', 'Entertainment', 'Join us for a movie night under the stars with free popcorn and drinks.', 'Campus Lawn')
    event12 = create_active_event(jane.id, 'Volunteer Fair', 'Community Service', 'Learn about volunteer opportunities on and off campus and sign up to make a difference in your community.', 'Student Center Lobby')
    event13 = create_active_event(jane.id, 'Hackathon', 'Technology', 'Collaborate with fellow students to develop innovative solutions to real-world problems in our 24-hour hackathon.', 'Engineering Building, Room 101')
    event14_start = now
    event14_end = now + timedelta(days=7)  # Event lasts for 7 days
    event14 = create_event(jane.id, 'Music Festival', 'Entertainment', 'Enjoy live performances from local bands and artists at our campus music festival.', event14_start, event14_end, 'Theather 1', None, True, 1)  # Example of an event with a limit
    # Give Bob some points for demo
    bob_obj = Student.query.filter_by(username='bob').first()
    if bob_obj:
        bob_obj.add_points(999)  # Give enough points for all badges and rewards
        db.session.commit()
        
        # Join Bob to ALL events and log attendance
        print("Now attempting to join events and log attendance for Bob...")
        for event in [ event1, event2, event3, event4, event5, event6, event7, event8, event9, event10, event11, event12]:
            if event:
                joined = join_event(bob_obj.id, event.id)
                if joined:
                    log_attendance(bob_obj.id, event.id, datetime.now())
                    print(f'Bob attended event: {event.id} - {event.name}')
                else:
                    print(f'Bob failed to join or log attendance for event: {event.id} - {event.name}')
            else:
                print(f'Failed to create event: {event}')

    alice_obj = Student.query.filter_by(username='alice').first()
    if alice_obj and event1:  # pick Orientation or any event
        join_event(alice_obj.id, event1.id)
        join_event(alice_obj.id, event14.id)  # Attempt to join the limited event to demonstrate limit functionality
        log_attendance(alice_obj.id, event1.id, datetime.now())
        print(f'Alice attended event: {event1.id} - {event1.name}')

        # Redeem ALL rewards for Bob
        for reward in [reward_1, reward_2, reward_3, reward_4, reward_5, KFC_Bucket, Starbucks_Gift_Card, Movie_Tickets, Massage_Coupon]:
            if reward:
                redeem_reward(bob_obj.id, reward.id, datetime.now() + timedelta(days=random.randint(1, 300)))  # Redeem with a random timestamp to demonstrate the student history page. Should be removed or modified for production use.
                print(f'Bob redeemed reward: {reward.name} for {reward.pointCost} points')
            else:
                print(f'Failed to create reward: {reward}')
        db.session.commit()
    else:
        print('Failed to create user Bob. Please check the user creation process.')