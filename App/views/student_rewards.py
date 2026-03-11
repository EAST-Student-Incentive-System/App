from flask import Blueprint, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity

from App.controllers.rewards import (
    viewReward,
    redeem_reward,
)
from App.controllers.redeemedReward import view_redeemed_rewards
from App.database import db
from App.models import Student

reward_student_views = Blueprint("reward_student_views", __name__, template_folder="../templates")


def _get_current_student():
    """Return the Student record for the currently logged-in user, or None."""
    identity = get_jwt_identity()
    if identity is None:
        return None
    try:
        student_id = int(identity)
    except (TypeError, ValueError):
        return None
    return db.session.get(Student, student_id)


# ─── Browse & Redeem ──────────────────────────────────────────────────────────

@reward_student_views.route("/student/rewards", methods=["GET"])
@jwt_required()
def student_rewards_page():
    """Show all active rewards with the student's redeemability flag."""
    student = _get_current_student()
    if not student:
        return render_template("401.html", error="Student account required."), 401

    rewards = viewReward(student.id)           # list of dicts with 'redeemable' key
    redeemed = view_redeemed_rewards(student.id)  # list of RedeemedReward objects

    return render_template(
        "student_rewards.html",
        user=student,
        student=student,
        rewards=rewards or [],
        redeemed_rewards=redeemed or [],
    )


@reward_student_views.route("/student/rewards/<int:reward_id>/redeem", methods=["POST"])
@jwt_required()
def redeem_reward_page(reward_id):
    """Process a reward redemption for the current student."""
    student = _get_current_student()
    if not student:
        return render_template("401.html", error="Student account required."), 401

    result = redeem_reward(student.id, reward_id)

    if result is None:
        flash("Reward or student not found.", "error")
    elif result is False:
        flash("Not enough points to redeem this reward.", "warning")
    else:
        flash("Reward redeemed successfully! 🎉", "success")

    return redirect(url_for("reward_student_views.student_rewards_page"))