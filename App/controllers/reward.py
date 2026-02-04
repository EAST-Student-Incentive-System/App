from App.models import Reward
from App.database import db


def create_reward(name, description, point_cost, active=True):
    reward = Reward(name=name, description=description, pointCost=point_cost, active=active)
    db.session.add(reward)
    db.session.commit()
    return reward

def update_reward(reward_id, name=None, description=None, point_cost=None):
    reward = db.session.get(Reward, reward_id)
    if not reward:
        return None
    if name:
        reward.set_name(name)
    if description:
        reward.set_description(description)
    if point_cost:
        reward.set_point_cost(point_cost)
    db.session.commit()
    return reward

def delete_reward(reward_id):
    reward = db.session.get(Reward, reward_id)
    if not reward:
        return False
    db.session.delete(reward)
    db.session.commit()
    return True

def toggle_reward(reward_id):
    reward = db.session.get(Reward, reward_id)
    if not reward:
        return None
    reward.toggle()
    return reward
