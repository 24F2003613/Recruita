from database import connect_recruita_database



def fetch_admin_profile(admin_id):
      recruita_db_connection = connect_recruita_database()
      try:
            return recruita_db_connection.execute(
                  "SELECT admin_id, name, email FROM admins WHERE admin_id = ?",
                  (admin_id,),
            ).fetchone()
      finally:
            recruita_db_connection.close()



def fetch_admin_dashboard_counts():
      recruita_db_connection = connect_recruita_database()
      try:
            return {
                  "students_total": recruita_db_connection.execute(
                        "SELECT COUNT(*) AS total FROM students"
                  ).fetchone()["total"],
                  "companies_total": recruita_db_connection.execute(
                        "SELECT COUNT(*) AS total FROM companies"
                  ).fetchone()["total"],
                  "drives_total": recruita_db_connection.execute(
                        "SELECT COUNT(*) AS total FROM placement_drives"
                  ).fetchone()["total"],
                  "applications_total": recruita_db_connection.execute(
                        "SELECT COUNT(*) AS total FROM applications"
                  ).fetchone()["total"],
            }
      finally:
            recruita_db_connection.close()



def fetch_companies_pending_approval():
      recruita_db_connection = connect_recruita_database()
      try:
            return recruita_db_connection.execute(
                  """
                  SELECT company_id, company_name, website, hr_name, phone, email, approval_status, is_active
                  FROM companies
                  WHERE approval_status = 'Pending'
                  ORDER BY company_id DESC
                  """
            ).fetchall()
      finally:
            recruita_db_connection.close()



def fetch_drives_pending_approval():
      recruita_db_connection = connect_recruita_database()
      try:
            return recruita_db_connection.execute(
                  """
                  SELECT d.drive_id, d.job_title, d.application_deadline, d.drive_status, c.company_name
                  FROM placement_drives d
                  JOIN companies c ON c.company_id = d.company_id
                  WHERE d.drive_status = 'Pending'
                  ORDER BY d.drive_id DESC
                  """
            ).fetchall()
      finally:
            recruita_db_connection.close()



def update_company_approval_status(company_id, approval_decision):
      recruita_db_connection = connect_recruita_database()
      try:
            recruita_db_connection.execute(
                  "UPDATE companies SET approval_status = ? WHERE company_id = ?",
                  (approval_decision, company_id),
            )
            recruita_db_connection.commit()
      finally:
            recruita_db_connection.close()



def update_drive_status(drive_id, next_status):
      recruita_db_connection = connect_recruita_database()
      try:
            recruita_db_connection.execute(
                  "UPDATE placement_drives SET drive_status = ? WHERE drive_id = ?",
                  (next_status, drive_id),
            )
            recruita_db_connection.commit()
      finally:
            recruita_db_connection.close()



def search_students_for_admin_panel(search_query):
      recruita_db_connection = connect_recruita_database()
      try:
            return recruita_db_connection.execute(
                  """
                  SELECT student_id, full_name, roll_number, department, email, is_active
                  FROM students
                  WHERE full_name LIKE ? OR roll_number LIKE ? OR department LIKE ?
                  ORDER BY student_id DESC
                  """,
                  (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"),
            ).fetchall()
      finally:
            recruita_db_connection.close()



def toggle_student_account_active_state(student_id):
      recruita_db_connection = connect_recruita_database()
      try:
            student_row = recruita_db_connection.execute(
                  "SELECT is_active FROM students WHERE student_id = ?",
                  (student_id,),
            ).fetchone()
            if not student_row:
                  return


            next_status = 0 if student_row["is_active"] == 1 else 1
            recruita_db_connection.execute(
                  "UPDATE students SET is_active = ? WHERE student_id = ?",
                  (next_status, student_id),
            )
            recruita_db_connection.commit()
      finally:
            recruita_db_connection.close()



def search_companies_for_admin_panel(search_query):
      recruita_db_connection = connect_recruita_database()
      try:
            return recruita_db_connection.execute(
                  """
                  SELECT company_id, company_name, website, hr_name, phone, email, approval_status, is_active
                  FROM companies
                  WHERE company_name LIKE ?
                  ORDER BY company_id DESC
                  """,
                  (f"%{search_query}%",),
            ).fetchall()
      finally:
            recruita_db_connection.close()



def toggle_company_account_active_state(company_id):
      recruita_db_connection = connect_recruita_database()
      try:
            company_row = recruita_db_connection.execute(
                  "SELECT is_active, approval_status FROM companies WHERE company_id = ?",
                  (company_id,),
            ).fetchone()
            if not company_row:
                  return False


            next_status = 0 if company_row["is_active"] == 1 else 1


            # Deactivation is treated as blacklisting. We keep approval as Rejected in DB
            # because the schema allows Pending/Approved/Rejected only.
            if next_status == 0:
                  recruita_db_connection.execute(
                        "UPDATE companies SET is_active = 0, approval_status = 'Rejected' WHERE company_id = ?",
                        (company_id,),
                  )
                  recruita_db_connection.commit()
                  return "blacklisted"


            if next_status == 1 and company_row["approval_status"] == "Rejected":
                  recruita_db_connection.execute(
                        "UPDATE companies SET is_active = 1, approval_status = 'Pending' WHERE company_id = ?",
                        (company_id,),
                  )
                  recruita_db_connection.commit()
                  return "reactivated_pending"


            recruita_db_connection.execute(
                  "UPDATE companies SET is_active = ? WHERE company_id = ?",
                  (next_status, company_id),
            )
            recruita_db_connection.commit()
            return "updated"
      finally:
            recruita_db_connection.close()



def fetch_all_drives_for_admin_panel():
      recruita_db_connection = connect_recruita_database()
      try:
            return recruita_db_connection.execute(
                  """
                  SELECT d.drive_id, d.job_title, d.application_deadline, d.drive_status, c.company_name
                  FROM placement_drives d
                  JOIN companies c ON c.company_id = d.company_id
                  ORDER BY d.drive_id DESC
                  """
            ).fetchall()
      finally:
            recruita_db_connection.close()



def fetch_all_applications_for_admin_panel():
      recruita_db_connection = connect_recruita_database()
      try:
            return recruita_db_connection.execute(
                  """
                  SELECT a.application_id, a.application_date, a.application_status,
                            s.full_name, s.roll_number, d.job_title, c.company_name
                  FROM applications a
                  JOIN students s ON s.student_id = a.student_id
                  JOIN placement_drives d ON d.drive_id = a.drive_id
                  JOIN companies c ON c.company_id = d.company_id
                  ORDER BY a.application_id DESC
                  """
            ).fetchall()
      finally:
            recruita_db_connection.close()
