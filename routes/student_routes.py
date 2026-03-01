from datetime import date
import sqlite3

from flask import abort, flash, redirect, render_template, request, session, url_for

from models.student_models import (
    create_student_drive_application,
    fetch_active_recruitment_drives,
    fetch_drive_for_application,
    fetch_existing_student_application,
    fetch_student_application_history,
    fetch_student_profile,
    update_student_profile,
)
from models.auth_models import require_student_role


def register_student_routes(app):
    @app.route("/student/profile")
    @require_student_role
    def student_profile():
        student_id = session.get("role_id")
        if not student_id:
            abort(403)

        student_profile_data = fetch_student_profile(student_id)
        if not student_profile_data or student_profile_data["is_active"] == 0:
            abort(403)

        return render_template("student/student_profile.html", student_profile_data=student_profile_data)

    @app.route("/student/dashboard")
    @require_student_role
    def student_dashboard():
        student_id = session.get("role_id")
        if not student_id:
            abort(403)

        student_profile = fetch_student_profile(student_id)
        if not student_profile or student_profile["is_active"] == 0:
            abort(403)

        return render_template(
            "student/student_dashboard.html",
            student_profile=student_profile,
            active_recruitment_drives=fetch_active_recruitment_drives(student_id, str(date.today())),
        )

    @app.route("/student/edit-profile", methods=["GET", "POST"])
    @require_student_role
    def student_edit_profile():
        student_id = session.get("role_id")
        if not student_id:
            abort(403)

        student_profile = fetch_student_profile(student_id)
        if not student_profile or student_profile["is_active"] == 0:
            abort(403)

        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            college = request.form.get("college", "").strip()
            department = request.form.get("department", "").strip()
            gpa = request.form.get("gpa", "").strip()
            resume = request.form.get("resume", "").strip()
            phone = request.form.get("phone", "").strip()
            email = request.form.get("email", "").strip()

            if not full_name or not college or not department or not gpa or not resume or not email:
                flash("All profile fields are required.", "danger")
                return redirect(url_for("student_edit_profile"))

            try:
                update_student_profile(
                    student_id,
                    {
                        "full_name": full_name,
                        "college": college,
                        "department": department,
                        "gpa": gpa,
                        "resume": resume,
                        "phone": phone if phone else None,
                        "email": email,
                    },
                )
                flash("Profile updated successfully.", "success")
                return redirect(url_for("student_dashboard"))
            except sqlite3.IntegrityError:
                flash("Email is already used by another account.", "danger")
                return redirect(url_for("student_edit_profile"))
            except Exception as db_error:
                print("Error while updating student profile:", db_error)

        return render_template("student/student_edit_profile.html", student_profile=student_profile)

    @app.route("/student/apply-drive/<int:drive_id>", methods=["POST"])
    @require_student_role
    def apply_drive(drive_id):
        student_id = session.get("role_id")
        if not student_id:
            abort(403)

        student_profile = fetch_student_profile(student_id)
        if not student_profile or student_profile["is_active"] == 0:
            abort(403)

        drive_for_application = fetch_drive_for_application(drive_id, str(date.today()))
        if not drive_for_application:
            return "This drive is not available for applications", 400

        existing_application = fetch_existing_student_application(student_id, drive_id)

        # Students are allowed to apply only once per drive.
        # This prevents duplicate entries and keeps shortlisting clean.
        if existing_application:
            return "You have already applied for this drive", 400

        try:
            create_student_drive_application(student_id, drive_id, str(date.today()))
        except sqlite3.IntegrityError as db_error:
            print("Error while storing student application:", db_error)
            return "Unable to apply right now", 400
        except Exception as db_error:
            print("Error while processing drive application:", db_error)
            return "Unable to apply right now", 500

        return redirect(url_for("student_dashboard"))

    @app.route("/student/application-history")
    @require_student_role
    def application_history():
        student_id = session.get("role_id")
        if not student_id:
            abort(403)

        return render_template(
            "student/student_application_history.html",
            student_drive_applications=fetch_student_application_history(student_id),
        )
