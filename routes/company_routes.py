from datetime import date

from flask import abort, flash, redirect, render_template, request, session, url_for

from models.company_models import (
    close_company_drive,
    create_company_drive,
    fetch_company_drive,
    fetch_company_drive_for_applications,
    fetch_company_drives,
    fetch_company_owned_application,
    fetch_company_profile,
    fetch_drive_applications,
    update_company_application_status,
    update_company_drive,
    update_company_profile,
)
from models.auth_models import require_company_role


def register_company_routes(app):
    @app.route("/company/profile")
    @require_company_role
    def company_profile():
        company_id = session.get("role_id")
        if not company_id:
            abort(403)

        company_profile_data = fetch_company_profile(company_id)
        if not company_profile_data or company_profile_data["is_active"] == 0:
            abort(403)

        return render_template("company/company_profile.html", company_profile_data=company_profile_data)

    @app.route("/company/dashboard")
    @require_company_role
    def company_dashboard():
        company_id = session.get("role_id")
        if not company_id:
            abort(403)

        company_profile = fetch_company_profile(company_id)
        if not company_profile or company_profile["is_active"] == 0:
            abort(403)

        return render_template(
            "company/company_dashboard.html",
            company_profile=company_profile,
            company_posted_drives=fetch_company_drives(company_id),
        )

    @app.route("/company/edit-profile", methods=["GET", "POST"])
    @require_company_role
    def company_edit_profile():
        company_id = session.get("role_id")
        if not company_id:
            abort(403)

        company_profile = fetch_company_profile(company_id)
        if not company_profile or company_profile["is_active"] == 0:
            abort(403)

        if request.method == "POST":
            company_name = request.form.get("company_name", "").strip()
            website = request.form.get("website", "").strip()
            hr_name = request.form.get("hr_name", "").strip()
            phone = request.form.get("phone", "").strip()
            email = request.form.get("email", "").strip()

            if not company_name or not website or not hr_name or not phone or not email:
                flash("All profile fields are required.", "danger")
                return redirect(url_for("company_edit_profile"))

            try:
                update_company_profile(
                    company_id,
                    {
                        "company_name": company_name,
                        "website": website,
                        "hr_name": hr_name,
                        "phone": phone,
                        "email": email,
                    },
                )
                flash("Company profile updated successfully.", "success")
                return redirect(url_for("company_dashboard"))
            except Exception as db_error:
                print("Error while updating company profile:", db_error)
                flash("Unable to update profile right now.", "danger")
                return redirect(url_for("company_edit_profile"))

        return render_template("company/company_edit_profile.html", company_profile=company_profile)

    @app.route("/company/create-drive", methods=["POST"])
    @require_company_role
    def create_drive():
        company_id = session.get("role_id")
        if not company_id:
            abort(403)

        job_title = request.form.get("job_title", "").strip()
        job_description = request.form.get("job_description", "").strip()
        eligibility_criteria = request.form.get("eligibility_criteria", "").strip()
        application_deadline = request.form.get("application_deadline", "").strip()

        if not all([job_title, job_description, eligibility_criteria, application_deadline]):
            return "All drive fields are required", 400

        try:
            parsed_deadline = date.fromisoformat(application_deadline)
        except ValueError:
            return "Invalid deadline date", 400

        if parsed_deadline < date.today():
            return "Deadline cannot be in the past", 400

        company_profile = fetch_company_profile(company_id)
        if not company_profile or company_profile["is_active"] == 0:
            abort(403)
        if company_profile["approval_status"] != "Approved":
            return "Company is not approved to create drives", 403

        try:
            create_company_drive(
                company_id,
                {
                    "job_title": job_title,
                    "job_description": job_description,
                    "eligibility_criteria": eligibility_criteria,
                    "application_deadline": application_deadline,
                },
            )
        except Exception as db_error:
            print("Error while creating placement drive:", db_error)
        return redirect(url_for("company_dashboard"))

    @app.route("/company/edit-drive/<int:drive_id>", methods=["GET", "POST"])
    @require_company_role
    def edit_drive(drive_id):
        company_id = session.get("role_id")
        if not company_id:
            abort(403)

        company_drive = fetch_company_drive(company_id, drive_id)
        if not company_drive:
            abort(403)

        if request.method == "POST":
            job_title = request.form.get("job_title", "").strip()
            job_description = request.form.get("job_description", "").strip()
            eligibility_criteria = request.form.get("eligibility_criteria", "").strip()
            application_deadline = request.form.get("application_deadline", "").strip()

            if not all([job_title, job_description, eligibility_criteria, application_deadline]):
                flash("All drive fields are required for update.", "danger")
                return redirect(url_for("edit_drive", drive_id=drive_id))

            try:
                parsed_deadline = date.fromisoformat(application_deadline)
            except ValueError:
                flash("Invalid deadline date.", "danger")
                return redirect(url_for("edit_drive", drive_id=drive_id))

            if parsed_deadline < date.today():
                flash("Deadline cannot be in the past.", "danger")
                return redirect(url_for("edit_drive", drive_id=drive_id))

            try:
                update_company_drive(
                    company_id,
                    drive_id,
                    {
                        "job_title": job_title,
                        "job_description": job_description,
                        "eligibility_criteria": eligibility_criteria,
                        "application_deadline": application_deadline,
                    },
                )
                flash("Placement drive updated.", "success")
                return redirect(url_for("company_dashboard"))
            except Exception as db_error:
                print("Error while editing placement drive:", db_error)

        return render_template("company/company_edit_drive.html", company_drive=company_drive)

    @app.route("/company/close-drive/<int:drive_id>", methods=["POST"])
    @require_company_role
    def close_drive(drive_id):
        company_id = session.get("role_id")
        if not company_id:
            abort(403)

        try:
            close_company_drive(company_id, drive_id)
        except Exception as db_error:
            print("Error while closing placement drive:", db_error)
        return redirect(url_for("company_dashboard"))

    @app.route("/company/view-applications/<int:drive_id>")
    @require_company_role
    def view_applications(drive_id):
        company_id = session.get("role_id")
        if not company_id:
            abort(403)

        selected_drive = fetch_company_drive_for_applications(company_id, drive_id)
        if not selected_drive:
            abort(403)

        return render_template(
            "company/company_view_applications.html",
            selected_drive=selected_drive,
            student_drive_applications=fetch_drive_applications(drive_id),
        )

    @app.route("/company/update-application-status/<int:application_id>", methods=["POST"])
    @require_company_role
    def update_application_status(application_id):
        company_id = session.get("role_id")
        if not company_id:
            abort(403)

        next_application_status = request.form.get("application_status", "").strip()
        if next_application_status not in {"Applied", "Shortlisted", "Selected", "Rejected"}:
            return "Invalid application status", 400

        company_owned_application = fetch_company_owned_application(application_id, company_id)
        if not company_owned_application:
            abort(403)

        try:
            update_company_application_status(application_id, next_application_status)
        except Exception as db_error:
            print("Error while updating application status:", db_error)

        return redirect(request.referrer or url_for("company_dashboard"))
