from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from App.database import db
from App.models import Staff, Student
import os
from datetime import datetime
from App.controllers.user import has_active_timeout

appeal_views = Blueprint("appeal_views", __name__, template_folder="../templates")


# -----------------------
# Helpers
# -----------------------
def _get_current_staff():
    staff_id = get_jwt_identity()
    return db.session.get(Staff, int(staff_id)) if staff_id is not None else None


def _get_current_student():
    student_id = get_jwt_identity()
    return db.session.get(Student, int(student_id)) if student_id is not None else None


def _ensure_student_has_status(student: Student):
    """
    Backwards-compatible: if older rows have NULL status, treat as pending iff appeal_desc exists.
    """
    if getattr(student, "appeal_status", None) is None:
        if student.appeal_desc:
            student.appeal_status = "pending"


# -----------------------
# STAFF: Appeals queue
# -----------------------
@appeal_views.route("/staff/appeals", methods=["GET"])
@jwt_required()
def staff_appeals_page():
    staff = _get_current_staff()
    if not staff or staff.role != "staff":
        flash("Unauthorized", "error")
        return redirect(url_for("auth_views.login_page"))

    # Show ONLY pending appeals (preferred once appeal_status exists).
    # Fallback: also include legacy rows where appeal_desc is set but status is NULL.
    appealed_students = db.session.scalars(
        db.select(Student).where(
            (Student.appeal_status == "pending") |
            ((Student.appeal_status.is_(None)) & (Student.appeal_desc.isnot(None)))
        )
    ).all()

    # Normalize any legacy rows in-memory (optional)
    for s in appealed_students:
        _ensure_student_has_status(s)

    return render_template("staff_appeals.html", user=staff, appeals=appealed_students)


@appeal_views.route("/staff/appeals/<int:student_id>/resolve", methods=["POST"])
@jwt_required()
def resolve_appeal_action(student_id):
    """
    action=approve  => reduce timeout by 1, mark approved, CLEAR appeal text/image (removes from queue)
    action=delete   => mark rejected, CLEAR appeal text/image (removes from queue)
    """
    staff = _get_current_staff()
    if not staff or staff.role != "staff":
        flash("Unauthorized", "error")
        return redirect(url_for("auth_views.login_page"))

    student = db.session.get(Student, student_id)
    if not student:
        flash("Student not found", "error")
        return redirect(url_for("appeal_views.staff_appeals_page"))

    action = request.form.get("action")  # "approve" or "delete"
    if action not in ("approve", "delete"):
        flash("Please select Approve or Delete, then click Save.", "error")
        return redirect(url_for("appeal_views.staff_appeals_page"))

    if action == "approve":
        student.timeout_count = max(0, int(student.timeout_count or 0) - 1)
        student.appeal_status = "approved"

        # Clear appeal so it disappears from staff queue (as requested)
        student.appeal_desc = None
        student.appeal_image = None
        student.timeout_until = None  # Clear timeout so student can immediately access pages again

        flash(f"Approved appeal for {student.username} (timeout reduced).", "success")

    elif action == "delete":
        student.appeal_status = "rejected"

        # Clear appeal so it disappears from staff queue (as requested)
        student.appeal_desc = None
        student.appeal_image = None

        flash(f"Rejected appeal for {student.username}.", "success")

    db.session.commit()
    return redirect(url_for("appeal_views.staff_appeals_page"))


# (Optional) Keep old endpoints working, but route them through resolve()
@appeal_views.route("/staff/appeals/<int:student_id>/delete", methods=["POST"])
@jwt_required()
def delete_appeal_action(student_id):
    # Treat delete as reject
    request.form = request.form.copy()
    request.form = request.form.to_dict(flat=True)
    # This endpoint exists for backward compatibility with older templates.
    # Prefer using /resolve going forward.
    staff = _get_current_staff()
    if not staff or staff.role != "staff":
        flash("Unauthorized", "error")
        return redirect(url_for("auth_views.login_page"))

    student = db.session.get(Student, student_id)
    if not student:
        flash("Student not found", "error")
        return redirect(url_for("appeal_views.staff_appeals_page"))

    student.appeal_status = "rejected"
    student.appeal_desc = None
    student.appeal_image = None
    db.session.commit()

    flash(f"Rejected appeal for {student.username}.", "success")
    return redirect(url_for("appeal_views.staff_appeals_page"))


@appeal_views.route("/staff/appeals/<int:student_id>/remove-timeout", methods=["POST"])
@jwt_required()
def remove_timeout_action(student_id):
    # Treat remove-timeout as approve, but keep endpoint for compatibility
    staff = _get_current_staff()
    if not staff or staff.role != "staff":
        flash("Unauthorized", "error")
        return redirect(url_for("auth_views.login_page"))

    student = db.session.get(Student, student_id)
    if not student:
        flash("Student not found", "error")
        return redirect(url_for("appeal_views.staff_appeals_page"))

    student.timeout_count = max(0, int(student.timeout_count or 0) - 1)
    student.appeal_status = "approved"
    student.appeal_desc = None
    student.appeal_image = None

    db.session.commit()
    flash(f"Approved appeal for {student.username} (timeout reduced).", "success")
    return redirect(url_for("appeal_views.staff_appeals_page"))


# -----------------------
# STUDENT: Appeal form
# -----------------------
@appeal_views.route("/student/appeal", methods=["GET"])
@jwt_required()
def student_appeal_page():
    student = _get_current_student()
    if not student or student.role != "student":
        flash("Unauthorized", "error")
        return redirect(url_for("auth_views.login_page"))
    
    if not has_active_timeout(student):
        flash("You do not have anything to appeal.", "error")
        return redirect(url_for("event_views.get_student_events_route"))

    
    if not student.timeout_until or student.timeout_until < datetime.utcnow():
        flash("You do not have anything to appeal.", "error")
        return redirect(url_for("event_views.get_student_events_route"))

    # Default status display
    if getattr(student, "appeal_status", None) is None and student.appeal_desc:
        student.appeal_status = "pending"
        db.session.commit()

    return render_template("student_appeal.html", user=student, student=student)


@appeal_views.route("/student/appeal", methods=["POST"])
@jwt_required()
def submit_student_appeal_action():
    student = _get_current_student()
    if not student or student.role != "student":
        flash("Unauthorized", "error")
        return redirect(url_for("auth_views.login_page"))
    
    if not has_active_timeout(student):
        flash("You do not have anything to appeal.", "error")
        return redirect(url_for("event_views.get_student_events_route"))

    
    if not student.timeout_until or student.timeout_until < datetime.utcnow():
        flash("You do not have anything to appeal.", "error")
        return redirect(url_for("event_views.get_student_events_route"))

    desc = (request.form.get("appeal_desc") or "").strip()
    image = request.files.get("appeal_image")

    if not desc:
        flash("Please enter a description for your appeal.", "error")
        return redirect(url_for("event_views.get_student_events_route"))

    filename = None
    if image and image.filename:
        filename = secure_filename(image.filename)
        upload_folder = os.path.join(current_app.static_folder, "uploads")
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        image.save(filepath)

    student.appeal_desc = desc
    student.appeal_status = "pending"
    if filename:
        student.appeal_image = filename

    db.session.commit()
    flash("Appeal submitted successfully.", "success")
    return redirect(url_for("appeal_views.student_appeal_page"))



#------------------------------------------
# API endpoints for Performance Testing or backend use (not meant for frontend/Jinja consumption)
#------------------------------------------


# STAFF: Get all pending appeals
@appeal_views.route("/api/staff/appeals", methods=["GET"])
@jwt_required()
def api_get_staff_appeals():
    staff = _get_current_staff()
    if not staff or staff.role != "staff":
        return {"error": "Unauthorized"}, 403

    appealed_students = db.session.scalars(
        db.select(Student).where(
            (Student.appeal_status == "pending") |
            ((Student.appeal_status.is_(None)) & (Student.appeal_desc.isnot(None)))
        )
    ).all()

    appeals_json = []
    for s in appealed_students:
        _ensure_student_has_status(s)
        appeals_json.append({
            "id": s.id,
            "username": s.username,
            "appeal_status": s.appeal_status,
            "appeal_desc": s.appeal_desc,
            "appeal_image": s.appeal_image
        })

    return {"appeals": appeals_json}, 200


# STAFF: Resolve appeal (approve or reject)
@appeal_views.route("/api/staff/appeals/<int:student_id>/resolve", methods=["POST"])
@jwt_required()
def api_resolve_appeal(student_id):
    staff = _get_current_staff()
    if not staff or staff.role != "staff":
        return {"error": "Unauthorized"}, 403

    student = db.session.get(Student, student_id)
    if not student:
        return {"error": "Student not found"}, 404

    action = request.json.get("action")
    if action not in ("approve", "delete"):
        return {"error": "Invalid action"}, 400

    if action == "approve":
        student.timeout_count = max(0, int(student.timeout_count or 0) - 1)
        student.appeal_status = "approved"
        student.appeal_desc = None
        student.appeal_image = None
        student.timeout_until = None
    elif action == "delete":
        student.appeal_status = "rejected"
        student.appeal_desc = None
        student.appeal_image = None

    db.session.commit()
    return {"success": True, "student_id": student.id, "appeal_status": student.appeal_status}, 200


# STUDENT: Submit appeal
@appeal_views.route("/api/student/appeal", methods=["POST"])
@jwt_required()
def api_submit_student_appeal():
    student = _get_current_student()
    if not student or student.role != "student":
        return {"error": "Unauthorized"}, 403

    if not has_active_timeout(student):
        return {"error": "No active timeout to appeal"}, 400

    desc = (request.json.get("appeal_desc") or "").strip()
    if not desc:
        return {"error": "Appeal description required"}, 400

    student.appeal_desc = desc
    student.appeal_status = "pending"
    db.session.commit()

    return {"success": True, "student_id": student.id, "appeal_status": student.appeal_status}, 201


# STUDENT: View appeal status
@appeal_views.route("/api/student/appeal", methods=["GET"])
@jwt_required()
def api_get_student_appeal():
    student = _get_current_student()
    if not student or student.role != "student":
        return {"error": "Unauthorized"}, 403

    return {
        "student_id": student.id,
        "username": student.username,
        "appeal_status": student.appeal_status,
        "appeal_desc": student.appeal_desc,
        "appeal_image": student.appeal_image
    }, 200
