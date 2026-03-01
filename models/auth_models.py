from functools import wraps

from flask import abort, session

from database import open_recruita_database


def require_admin_role(view_function):
    @wraps(view_function)
    def admin_guard(*args, **kwargs):
        if session.get("user_role") != "admin":
            abort(403)
        return view_function(*args, **kwargs)

    return admin_guard


def require_company_role(view_function):
    @wraps(view_function)
    def company_guard(*args, **kwargs):
        if session.get("user_role") != "company":
            abort(403)
        return view_function(*args, **kwargs)

    return company_guard


def require_student_role(view_function):
    @wraps(view_function)
    def student_guard(*args, **kwargs):
        if session.get("user_role") != "student":
            abort(403)
        return view_function(*args, **kwargs)

    return student_guard


def fetch_admin_account_by_email(email):
    placement_db_connection = open_recruita_database()
    try:
        return placement_db_connection.execute(
            "SELECT admin_id, name, email, password_hash FROM admins WHERE email = ?",
            (email,),
        ).fetchone()
    finally:
        placement_db_connection.close()


def fetch_company_account_by_email(email):
    placement_db_connection = open_recruita_database()
    try:
        return placement_db_connection.execute(
            """
            SELECT company_id, company_name, email, password_hash, approval_status, is_active
            FROM companies
            WHERE email = ?
            """,
            (email,),
        ).fetchone()
    finally:
        placement_db_connection.close()


def fetch_student_account_by_identifier(login_identifier):
    placement_db_connection = open_recruita_database()
    try:
        return placement_db_connection.execute(
            """
            SELECT student_id, full_name, roll_number, email, password_hash, is_active
            FROM students
            WHERE email = ? OR roll_number = ?
            """,
            (login_identifier, login_identifier),
        ).fetchone()
    finally:
        placement_db_connection.close()


def create_student_registration(student_data):
    placement_db_connection = open_recruita_database()
    try:
        placement_db_connection.execute(
            """
            INSERT INTO students (
                full_name, roll_number, college, department, gpa, resume, phone,
                email, password_hash, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                student_data["full_name"],
                student_data["roll_number"],
                student_data["college"],
                student_data["department"],
                student_data["gpa"],
                student_data["resume"],
                student_data["phone"],
                student_data["email"],
                student_data["password"],
            ),
        )
        placement_db_connection.commit()
    finally:
        placement_db_connection.close()


def create_company_registration(company_data):
    placement_db_connection = open_recruita_database()
    try:
        placement_db_connection.execute(
            """
            INSERT INTO companies (
                company_name, website, hr_name, phone, email,
                password_hash, approval_status, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, 'Pending', 1)
            """,
            (
                company_data["company_name"],
                company_data["website"],
                company_data["hr_name"],
                company_data["phone"],
                company_data["email"],
                company_data["password"],
            ),
        )
        placement_db_connection.commit()
    finally:
        placement_db_connection.close()
