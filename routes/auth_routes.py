import sqlite3

from flask import flash, redirect, render_template, request, session, url_for

from models.auth_models import (
    create_company_registration,
    create_student_registration,
    fetch_admin_account_by_email,
    fetch_company_account_by_email,
    fetch_student_account_by_identifier,
)


def register_auth_routes(app):
    @app.route("/")
    def home():
        if session.get("user_role") == "admin":
            return redirect(url_for("admin_dashboard"))
        if session.get("user_role") == "company":
            return redirect(url_for("company_dashboard"))
        if session.get("user_role") == "student":
            return redirect(url_for("student_dashboard"))

        auth_view = request.args.get("view", "login").strip().lower()
        if auth_view not in {"login", "register"}:
            auth_view = "login"

        selected_registration_role = request.args.get("register_role", "student").strip().lower()
        if selected_registration_role not in {"student", "company"}:
            selected_registration_role = "student"

        return render_template(
            "auth/authentication.html",
            auth_view=auth_view,
            selected_registration_role=selected_registration_role,
        )

    @app.route("/login", methods=["POST"])
    def login():
        login_identifier = request.form.get("login_identifier", "").strip()
        login_password = request.form.get("login_password", "").strip()

        if not login_identifier or not login_password:
            flash("Enter email/username and password to continue.", "danger")
            return redirect(url_for("home", view="login"))

        try:
            admin_account = fetch_admin_account_by_email(login_identifier)
            if admin_account and admin_account["password_hash"] == login_password:
                session.clear()
                session["user_role"] = "admin"
                session["role_id"] = admin_account["admin_id"]
                session["display_name"] = admin_account["name"]
                return redirect(url_for("admin_dashboard"))

            company_account = fetch_company_account_by_email(login_identifier)
            if company_account and company_account["password_hash"] == login_password:
                if company_account["is_active"] == 0:
                    flash("Company account is inactive. Contact placement cell.", "danger")
                    return redirect(url_for("home", view="login"))
                if company_account["approval_status"] == "Pending":
                    flash("Company is pending admin approval. Login will be enabled after approval.", "warning")
                    return redirect(url_for("home", view="login"))
                if company_account["approval_status"] == "Rejected":
                    flash("Company registration was rejected by admin.", "danger")
                    return redirect(url_for("home", view="login"))

                session.clear()
                session["user_role"] = "company"
                session["role_id"] = company_account["company_id"]
                session["display_name"] = company_account["company_name"]
                return redirect(url_for("company_dashboard"))

            student_account = fetch_student_account_by_identifier(login_identifier)
            if student_account and student_account["password_hash"] == login_password:
                if student_account["is_active"] == 0:
                    flash("Student account is inactive. Contact placement cell.", "danger")
                    return redirect(url_for("home", view="login"))

                session.clear()
                session["user_role"] = "student"
                session["role_id"] = student_account["student_id"]
                session["display_name"] = student_account["full_name"]
                return redirect(url_for("student_dashboard"))
        except Exception as db_error:
            print("Error while processing login:", db_error)
            flash("Unable to login right now. Please try again.", "danger")
            return redirect(url_for("home", view="login"))

        flash("Invalid credentials or account not found.", "danger")
        return redirect(url_for("home", view="login"))

    @app.route("/register", methods=["POST"])
    def register():
        registration_role = request.form.get("registration_role", "").strip()
        account_email = request.form.get("account_email", "").strip()
        account_password = request.form.get("account_password", "").strip()

        if registration_role not in {"student", "company"}:
            flash("Choose Student or Company for registration.", "danger")
            return redirect(url_for("home", view="register"))

        if not account_email or not account_password:
            flash("Email and password fields are required.", "danger")
            return redirect(url_for("home", view="register", register_role=registration_role))

        try:
            if registration_role == "student":
                student_full_name = request.form.get("student_full_name", "").strip()
                student_college = request.form.get("student_college", "").strip()
                student_department = request.form.get("student_department", "").strip()
                student_gpa = request.form.get("student_gpa", "").strip()
                student_resume = request.form.get("student_resume", "").strip()
                student_phone = request.form.get("student_phone", "").strip()

                if (
                    not student_full_name
                    or not student_college
                    or not student_department
                    or not student_gpa
                    or not student_resume
                ):
                    flash("Fill all required student fields.", "danger")
                    return redirect(url_for("home", view="register", register_role="student"))

                create_student_registration(
                    {
                        "full_name": student_full_name,
                        "roll_number": account_email.split("@")[0].upper(),
                        "college": student_college,
                        "department": student_department,
                        "gpa": student_gpa,
                        "resume": student_resume,
                        "phone": student_phone if student_phone else None,
                        "email": account_email,
                        "password": account_password,
                    }
                )
                flash("Student account created. You can login now.", "success")
                return redirect(url_for("home", view="login"))

            company_name = request.form.get("company_name", "").strip()
            company_website = request.form.get("company_website", "").strip()
            hr_name = request.form.get("hr_name", "").strip()
            company_phone = request.form.get("company_phone", "").strip()

            if not company_name or not company_website or not hr_name or not company_phone:
                flash("Fill all required company fields.", "danger")
                return redirect(url_for("home", view="register", register_role="company"))

            create_company_registration(
                {
                    "company_name": company_name,
                    "website": company_website,
                    "hr_name": hr_name,
                    "phone": company_phone,
                    "email": account_email,
                    "password": account_password,
                }
            )
            flash("Company registered. Login allowed only after admin approval.", "warning")
            return redirect(url_for("home", view="login"))
        except sqlite3.IntegrityError:
            flash("Email already exists.", "danger")
            return redirect(url_for("home", view="register", register_role=registration_role))
        except Exception as db_error:
            print("Error while registering account:", db_error)
            flash("Unable to register right now. Please try again.", "danger")
            return redirect(url_for("home", view="register", register_role=registration_role))

    @app.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        return redirect(url_for("home"))
