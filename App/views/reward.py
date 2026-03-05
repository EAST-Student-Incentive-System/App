from flask import Blueprint, jsonify, request

from App.controllers.rewards import (
    create_reward, get_reward, get_all_rewards_json, get_all_rewards,
    get_active_rewards, update_reward, delete_reward, toggle_reward,
    redeem_reward, viewReward, viewRewardHistory
)
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.models import User
from werkzeug.utils import secure_filename
from App.database import db
from App.models import Staff, Reward
import os
from flask import current_app

reward_views = Blueprint('reward_views', __name__, template_folder='../templates')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'App/static/uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




@reward_views.route('/rewards/active', methods=['GET'])
@jwt_required()
def active_rewards_api():
    rewards = get_active_rewards()
    return jsonify([r.get_json() for r in rewards] if rewards else [])


@reward_views.route('/reward/<int:reward_id>', methods=['GET'])
@jwt_required()
def get_reward_api(reward_id):
    r = get_reward(reward_id)
    if not r:
        return jsonify(message='Not found'), 404
    return jsonify(r.get_json())



@reward_views.route('/rewards/<int:reward_id>/redeem', methods=['POST'])
@jwt_required()
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


@reward_views.route('/students/<int:student_id>/rewards', methods=['GET'])
@jwt_required()
def view_rewards_for_student_api(student_id):
    res = viewReward(student_id)
    if res is None:
        return jsonify(message='student not found'), 404
    return jsonify(res)



#----------------- Staff Reward Management ----------------

@reward_views.route('/staff/<int:staff_id>/rewards', methods=['GET'])
@jwt_required()
def reward_history_page(staff_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'staff' or user.get('id') != staff_id:
        flash('Unauthorized', 'error')
        return redirect(url_for('reward_views.list_rewards_page'))
    res = viewRewardHistory(staff_id)
    return render_template('staff_rewards.html', rewards=res or [])

@reward_views.route('/rewards/new', methods=['GET', 'POST'])
@jwt_required()
def create_reward_page():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'staff':
        flash('Unauthorized', 'error')
        return redirect(url_for('reward_views.list_rewards_page'))

    if request.method == 'GET':
        return render_template('edit_reward.html', reward=None)

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        point_cost_str = request.form.get('point_cost')
        active = True if request.form.get('active') == 'on' else False

        # Validate point_cost before converting
        if not point_cost_str:
            flash('Point cost is required', 'error')
            return redirect(url_for('reward_views.create_reward_page'))

        try:
            point_cost = int(point_cost_str)
        except ValueError:
            flash('Point cost must be a number', 'error')
            return redirect(url_for('reward_views.create_reward_page'))

        # Call your controller function
        create_reward(name, description, point_cost, active)
        flash('Reward created successfully!', 'success')
        return redirect(url_for('reward_views.list_rewards_page'))



@reward_views.route("/rewards/<int:reward_id>", methods=["GET", "POST"])
@jwt_required()
def update_reward_page(reward_id):
    print("UPDATE REWARD PAGE HIT")
    user_id = get_jwt_identity()
    user = Staff.query.get(user_id)
    if not user or user.role != "staff":
        print("Unauthorized access attempt by user_id:", user_id)
        flash("Unauthorized", "error")
        return redirect(url_for("reward_views.list_rewards_page"))

    reward_obj = Reward.query.get(reward_id)
    if not reward_obj:
        print("Reward not found with id:", reward_id)
        flash("Reward not found", "error")
        return redirect(url_for("reward_views.list_rewards_page"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        point_cost = request.form.get("point_cost")  # match template field name
        active = True if request.form.get("active") == "on" else False
        image_file = request.files.get("image")

        if not all([name, description, point_cost]):
            print("Validation failed: Missing fields")
            flash("All fields are required", "error")
            return redirect(url_for("reward_views.update_reward_page", reward_id=reward_id))

        try:
            print("Updating reward with data:", name, description, point_cost, active)
            reward_obj.name = name
            reward_obj.description = description
            reward_obj.pointCost = int(point_cost)
            reward_obj.active = active

            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                filepath = os.path.join(current_app.static_folder, "uploads", filename)
                image_file.save(filepath)
                reward_obj.image = filename

            db.session.commit()
            flash("Reward updated successfully!", "success")
            return redirect(url_for("reward_views.list_rewards_page"))

        except ValueError as e:
            flash(f"Error updating reward: {e}", "error")
            return redirect(url_for("reward_views.update_reward_page", reward_id=reward_id))

    # GET request → render edit form
    print("Reached GET for update_reward_page with reward:")
    return render_template("edit_reward.html", reward=reward_obj)
 

@reward_views.route('/rewards/<int:reward_id>/delete', methods=['POST'])
@jwt_required()
def delete_reward_page(reward_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'staff':
        flash('Unauthorized', 'error')
        return redirect(url_for('reward_views.list_rewards_page'))
    ok = delete_reward(reward_id)
    if not ok:
        flash('Reward not found', 'error')
    else:
        flash('Reward deleted', 'success')
    return redirect(url_for('reward_views.list_rewards_page'))


@reward_views.route('/rewards/<int:reward_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_reward_page(reward_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'staff':
        flash('Unauthorized', 'error')
        return redirect(url_for('reward_views.list_rewards_page'))
    r = toggle_reward(reward_id)
    if not r:
        flash('Reward not found', 'error')
    else:
        flash(f'Reward {"activated" if r.active else "deactivated"}', 'success')
    return redirect(url_for('reward_views.list_rewards_page'))

@reward_views.route('/rewards', methods=['GET'])
@jwt_required()
def list_rewards_page():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'staff':
        flash('Unauthorized', 'error')
        return redirect(url_for('auth_views.login_page'))
    rewards = get_all_rewards()
    return render_template('staff_reward.html', rewards=rewards or [])


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