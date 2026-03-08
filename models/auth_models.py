from functools import wraps
from flask import abort, session
from database import connect_recruita_database
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

def fetch_admin_login_account(email):
      recruita_db_connection = connect_recruita_database()
      try:
            return recruita_db_connection.execute(
                  "SELECT admin_id, name, email, password_hash FROM admins WHERE email = ?",
                  (email,),
            ).fetchone()
      finally:
            recruita_db_connection.close()

def fetch_company_login_account(email):
      recruita_db_connection = connect_recruita_database()
      try:
            return recruita_db_connection.execute(
                  """
                  SELECT company_id, company_name, email, password_hash, approval_status, is_active
                  FROM companies
                  WHERE email = ?
                  """,
                  (email,),
            ).fetchone()
      finally:
            recruita_db_connection.close()

def fetch_student_login_account(login_identifier):
      recruita_db_connection = connect_recruita_database()
      try:
            return recruita_db_connection.execute(
                  """
                  SELECT student_id, full_name, roll_number, email, password_hash, is_active
                  FROM students
                  WHERE email = ? OR roll_number = ?
                  """,
                  (login_identifier, login_identifier),
            ).fetchone()
      finally:
            recruita_db_connection.close()
            
def create_student_account(student_data):
      recruita_db_connection = connect_recruita_database()
      try:
            recruita_db_connection.execute(
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
            recruita_db_connection.commit()
      finally:
            recruita_db_connection.close()
def create_company_account(company_data):
      recruita_db_connection = connect_recruita_database()
      try:
            recruita_db_connection.execute(
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
            recruita_db_connection.commit()
      finally:
            recruita_db_connection.close()
