from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.database import db
from App.models import Staff, Student

appeal_views = Blueprint("appeal_views", __name__, template_folder="../templates")


def _get_current_staff():
    staff_id = get_jwt_identity()
    return db.session.get(Staff, int(staff_id)) if staff_id is not None else None


@appeal_views.route("/staff/appeals", methods=["GET"])
@jwt_required()
def staff_appeals_page():
    staff = _get_current_staff()
    if not staff or staff.role != "staff":
        flash("Unauthorized", "error")
        return redirect(url_for("auth_views.login_page"))

    # Only show students who actually submitted an appeal
    appealed_students = db.session.scalars(
        db.select(Student).where(Student.appeal_desc.isnot(None))
    ).all()

    return render_template(
        "staff_appeals.html",
        user=staff,
        appeals=appealed_students
    )


@appeal_views.route("/staff/appeals/<int:student_id>/delete", methods=["POST"])
@jwt_required()
def delete_appeal_action(student_id):
    staff = _get_current_staff()
    if not staff or staff.role != "staff":
        flash("Unauthorized", "error")
        return redirect(url_for("auth_views.login_page"))

    student = db.session.get(Student, student_id)
    if not student:
        flash("Student not found", "error")
        return redirect(url_for("appeal_views.staff_appeals_page"))

    student.appeal_desc = None
    student.appeal_image = None
    db.session.commit()
    flash(f"Appeal removed for {student.username}", "success")
    return redirect(url_for("appeal_views.staff_appeals_page"))


@appeal_views.route("/staff/appeals/<int:student_id>/remove-timeout", methods=["POST"])
@jwt_required()
def remove_timeout_action(student_id):
    staff = _get_current_staff()
    if not staff or staff.role != "staff":
        flash("Unauthorized", "error")
        return redirect(url_for("auth_views.login_page"))

    student = db.session.get(Student, student_id)
    if not student:
        flash("Student not found", "error")
        return redirect(url_for("appeal_views.staff_appeals_page"))

    # Reduce timeout count by one (minimum 0)
    student.timeout_count = max(0, int(student.timeout_count or 0) - 1)

    # If you *do* have a timeout_date field in your codebase, add:
    # student.timeout_date = None

    db.session.commit()
    flash(f"Timeout reduced for {student.username}", "success")
    return redirect(url_for("appeal_views.staff_appeals_page"))

@appeal_views.route("/staff/appeals/<int:student_id>/resolve", methods=["POST"])
@jwt_required()
def resolve_appeal_action(student_id):
    staff = _get_current_staff()
    if not staff or staff.role != "staff":
        flash("Unauthorized", "error")
        return redirect(url_for("auth_views.login_page"))

    student = db.session.get(Student, student_id)
    if not student:
        flash("Student not found", "error")
        return redirect(url_for("appeal_views.staff_appeals_page"))

    action = request.form.get("action")  # expected: "approve" or "delete"
    if action not in ("approve", "delete"):
        flash("Please select Approve or Delete, then click Save.", "error")
        return redirect(url_for("appeal_views.staff_appeals_page"))

    if action == "approve":
        student.timeout_count = max(0, int(student.timeout_count or 0) - 1)
        # optionally also clear appeal from queue after approval:
        student.appeal_desc = None
        student.appeal_image = None
        flash(f"Approved appeal for {student.username} (timeout reduced).", "success")

    elif action == "delete":
        student.appeal_desc = None
        student.appeal_image = None
        flash(f"Deleted appeal for {student.username}.", "success")

    db.session.commit()
    return redirect(url_for("appeal_views.staff_appeals_page"))