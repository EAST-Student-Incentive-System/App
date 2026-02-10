from App.models import Reward, Student, RedeemedReward
from App.database import db


# Reward CRUD


def create_reward(name, description, point_cost, active=True):
    reward = Reward(name=name, description=description, pointCost=point_cost, active=active)
    db.session.add(reward)
    db.session.commit()
    return reward


def get_reward(reward_id):
    return db.session.get(Reward, reward_id)


def get_all_rewards():
    return db.session.scalars(db.select(Reward)).all()


def get_all_rewards_json():
    rewards = get_all_rewards()
    return [r.get_json() for r in rewards] if rewards else []


def get_active_rewards():
    return db.session.scalars(db.select(Reward).filter_by(active=True)).all()


def update_reward(reward_id, **kwargs):
    """Update a Reward using keyword arguments.

    Example: `update_reward(1, name='New', point_cost=50, active=False)`
    Accepts snake_case keys and maps `point_cost` -> `pointCost`.
    Keys with value `None` are skipped.
    """
    reward = db.session.get(Reward, reward_id)
    if not reward:
        return None

    field_map = {
        'point_cost': 'pointCost',
        'created_by': 'created_by',
        'active': 'active',
        'name': 'name',
        'description': 'description',
    }

    for key, value in kwargs.items():
        if value is None:
            continue
        model_attr = field_map.get(key, key)
        if hasattr(reward, model_attr):
            setattr(reward, model_attr, value)

    db.session.commit()
    return reward


"""def delete_reward(reward_id):
    reward = db.session.get(Reward, reward_id)
    if not reward:
        return False
    db.session.delete(reward)
    db.session.commit()
    return True"""    # commented out delete since we are just toggling active status instead of deleting records


def toggle_reward(reward_id):
    reward = db.session.get(Reward, reward_id)
    if not reward:
        return None
    # Reward.toggle commits inside the model; keep that behaviour
    reward.toggle()
    return reward


def redeem_reward(student_id, reward_id):
    student = db.session.get(Student, student_id)
    reward = db.session.get(Reward, reward_id)
    if not student or not reward:
        return None
    if not reward.isRedeemable(student.current_balance):
        return False
    # attempt to subtract points from student
    success = student.subtract_points(reward.pointCost)
    if not success:
        return False
    redeemed = RedeemedReward(student_id=student.id, reward_id=reward.id)
    db.session.add(redeemed)
    db.session.commit()
    return redeemed


def viewReward(student_id):
    #Return all active rewards with redeemable flag for given student.
    student = db.session.get(Student, student_id)
    if not student:
        return None
    rewards = get_active_rewards()
    result = []
    for r in rewards:
        data = r.get_json()
        data['redeemable'] = r.isRedeemable(student.current_balance)
        result.append(data)
    # sort by point cost ascending
    result.sort(key=lambda x: x.get('pointCost', 0))
    return result


def viewRewardHistory(staff_id):
    #Return all rewards created by a staff member (active or not).
    rewards = db.session.scalars(db.select(Reward).filter_by(created_by=staff_id)).all()
    return [r.get_json() for r in rewards] if rewards else []

#test

