from flask import Blueprint, jsonify, request

from App.controllers.rewards import (
    create_reward, get_reward, get_all_rewards_json, get_all_rewards,
    get_active_rewards, update_reward, delete_reward, toggle_reward,
    redeem_reward, viewReward, viewRewardHistory
)
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity

reward_views = Blueprint('reward_views', __name__, template_folder='../templates')


@reward_views.route('/api/rewards', methods=['GET'])
def list_rewards_api():
    # default to JSON list
    return jsonify(get_all_rewards_json())


@reward_views.route('/api/rewards/active', methods=['GET'])
def active_rewards_api():
    rewards = get_active_rewards()
    return jsonify([r.get_json() for r in rewards] if rewards else [])


@reward_views.route('/api/rewards/<int:reward_id>', methods=['GET'])
def get_reward_api(reward_id):
    r = get_reward(reward_id)
    if not r:
        return jsonify(message='Not found'), 404
    return jsonify(r.get_json())


@reward_views.route('/api/rewards', methods=['POST'])
def create_reward_api():
    data = request.json or {}
    name = data.get('name')
    description = data.get('description')
    point_cost = data.get('pointCost') or data.get('point_cost')
    active = data.get('active', True)
    if not name or point_cost is None:
        return jsonify(message='name and pointCost required'), 400
    r = create_reward(name, description or '', int(point_cost), active=bool(active))
    return jsonify(r.get_json()), 201


@reward_views.route('/api/rewards/<int:reward_id>', methods=['PUT'])
def update_reward_api(reward_id):
    data = request.json or {}
    kwargs = {}
    if 'name' in data:
        kwargs['name'] = data.get('name')
    if 'description' in data:
        kwargs['description'] = data.get('description')
    if 'pointCost' in data:
        kwargs['point_cost'] = data.get('pointCost')
    if 'point_cost' in data:
        kwargs['point_cost'] = data.get('point_cost')
    if 'active' in data:
        kwargs['active'] = data.get('active')
    r = update_reward(reward_id, **kwargs)
    if not r:
        return jsonify(message='Not found'), 404
    return jsonify(r.get_json())


@reward_views.route('/api/rewards/<int:reward_id>', methods=['DELETE'])
def delete_reward_api(reward_id):
    ok = delete_reward(reward_id)
    if not ok:
        return jsonify(message='Not found'), 404
    return jsonify(message='deleted')


@reward_views.route('/api/rewards/<int:reward_id>/toggle', methods=['POST'])
def toggle_reward_api(reward_id):
    r = toggle_reward(reward_id)
    if not r:
        return jsonify(message='Not found'), 404
    return jsonify(r.get_json())


@reward_views.route('/api/rewards/<int:reward_id>/redeem', methods=['POST'])
def redeem_reward_api(reward_id):
    data = request.json or {}
    student_id = data.get('student_id') or data.get('studentId')
    if student_id is None:
        return jsonify(message='student_id required'), 400
    res = redeem_reward(int(student_id), reward_id)
    if res is None:
        return jsonify(message='student or reward not found'), 404
    if res is False:
        return jsonify(message='not redeemable or insufficient balance'), 400
    return jsonify({'redeemed_id': res.id}), 201


@reward_views.route('/api/students/<int:student_id>/rewards', methods=['GET'])
def view_rewards_for_student_api(student_id):
    res = viewReward(student_id)
    if res is None:
        return jsonify(message='student not found'), 404
    return jsonify(res)


@reward_views.route('/api/staff/<int:staff_id>/rewards', methods=['GET'])
def reward_history_api(staff_id):
    res = viewRewardHistory(staff_id)
    return jsonify(res if res is not None else [])


''''@reward.route("/rewards", methods=["GET"])
@jwt_required()
def view_rewards():

    search = request.args.get("search")
    status = request.args.get("status", "all")

    rewards = rewards_service.get_all_rewards(search, status)

    return render_template(
        "rewards.html",
        rewards=rewards,
        search=search,
        status=status
    )


@reward.route("/rewards/<int:reward_id>/edit", methods=["GET"])
@jwt_required()
def edit_reward_page(reward_id):

    reward_obj = rewards_service.get_reward(reward_id)

    if not reward_obj:
        flash("Reward not found", "error")
        return redirect(url_for("reward.view_rewards"))

    return render_template(
        "reward_edit.html",
        reward=reward_obj
    )


@reward.route("/rewards/<int:reward_id>/edit", methods=["POST"])
@jwt_required()
def update_reward_route(reward_id):

    name = request.form.get("name")
    description = request.form.get("description")
    point_cost = request.form.get("point_cost")
    active = True if request.form.get("active") == "on" else False

    rewards_service.update_reward(
        reward_id,
        name=name,
        description=description,
        point_cost=point_cost,
        active=active
    )

    flash("Reward updated successfully!", "success")
    return redirect(url_for("reward.view_rewards"))

'''