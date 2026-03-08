from database import connect_recruita_database



def fetch_company_profile(company_id):
      recruita_db_connection = connect_recruita_database()
      try:
            return recruita_db_connection.execute(
                  """
                  SELECT company_id, company_name, website, hr_name, phone, email, approval_status, is_active
                  FROM companies
                  WHERE company_id = ?
                  """,
                  (company_id,),
            ).fetchone()
      finally:
            recruita_db_connection.close()



def update_company_profile(company_id, profile_data):
      recruita_db_connection = connect_recruita_database()
      try:
            recruita_db_connection.execute(
                  """
                  UPDATE companies
                  SET company_name = ?, website = ?, hr_name = ?, phone = ?, email = ?
                  WHERE company_id = ?
                  """,
                  (
                        profile_data["company_name"],
                        profile_data["website"],
                        profile_data["hr_name"],
                        profile_data["phone"],
                        profile_data["email"],
                        company_id,
                  ),
            )
            recruita_db_connection.commit()
      finally:
            recruita_db_connection.close()



def fetch_company_drive_records(company_id):
      recruita_db_connection = connect_recruita_database()
      try:
            return recruita_db_connection.execute(
                  """
                  SELECT drive_id, job_title, job_description, eligibility_criteria, application_deadline, drive_status
                  FROM placement_drives
                  WHERE company_id = ?
                  ORDER BY drive_id DESC
                  """,
                  (company_id,),
            ).fetchall()
      finally:
            recruita_db_connection.close()



def create_company_placement_drive(company_id, drive_data):
      recruita_db_connection = connect_recruita_database()
      try:
            recruita_db_connection.execute(
                  """
                  INSERT INTO placement_drives (
                        company_id, job_title, job_description, eligibility_criteria,
                        application_deadline, drive_status
                  ) VALUES (?, ?, ?, ?, ?, 'Pending')
                  """,
                  (
                        company_id,
                        drive_data["job_title"],
                        drive_data["job_description"],
                        drive_data["eligibility_criteria"],
                        drive_data["application_deadline"],
                  ),
            )
            recruita_db_connection.commit()
      finally:
            recruita_db_connection.close()



def fetch_company_drive_by_id(company_id, drive_id):
      recruita_db_connection = connect_recruita_database()
      try:
            return recruita_db_connection.execute(
                  """
                  SELECT drive_id, job_title, job_description, eligibility_criteria, application_deadline, drive_status
                  FROM placement_drives
                  WHERE drive_id = ? AND company_id = ?
                  """,
                  (drive_id, company_id),
            ).fetchone()
      finally:
            recruita_db_connection.close()



def update_company_drive_details(company_id, drive_id, drive_data):
      recruita_db_connection = connect_recruita_database()
      try:
            recruita_db_connection.execute(
                  """
                  UPDATE placement_drives
                  SET job_title = ?, job_description = ?, eligibility_criteria = ?, application_deadline = ?
                  WHERE drive_id = ? AND company_id = ?
                  """,
                  (
                        drive_data["job_title"],
                        drive_data["job_description"],
                        drive_data["eligibility_criteria"],
                        drive_data["application_deadline"],
                        drive_id,
                        company_id,
                  ),
            )
            recruita_db_connection.commit()
      finally:
            recruita_db_connection.close()



def close_company_drive_by_id(company_id, drive_id):
      recruita_db_connection = connect_recruita_database()
      try:
            recruita_db_connection.execute(
                  """
                  UPDATE placement_drives
                  SET drive_status = 'Closed'
                  WHERE drive_id = ? AND company_id = ?
                  """,
                  (drive_id, company_id),
            )
            recruita_db_connection.commit()
      finally:
            recruita_db_connection.close()



def fetch_company_drive_brief_for_applications(company_id, drive_id):
      recruita_db_connection = connect_recruita_database()
      try:
            return recruita_db_connection.execute(
                  "SELECT drive_id, job_title FROM placement_drives WHERE drive_id = ? AND company_id = ?",
                  (drive_id, company_id),
            ).fetchone()
      finally:
            recruita_db_connection.close()



def fetch_applications_for_company_drive(drive_id):
      recruita_db_connection = connect_recruita_database()
      try:
            return recruita_db_connection.execute(
                  """
                  SELECT a.application_id, a.application_date, a.application_status,
                            s.student_id, s.full_name, s.roll_number, s.department
                  FROM applications a
                  JOIN students s ON s.student_id = a.student_id
                  WHERE a.drive_id = ?
                  ORDER BY a.application_id DESC
                  """,
                  (drive_id,),
            ).fetchall()
      finally:
            recruita_db_connection.close()



def fetch_company_owned_application_record(application_id, company_id):
      recruita_db_connection = connect_recruita_database()
      try:
            return recruita_db_connection.execute(
                  """
                  SELECT a.application_id
                  FROM applications a
                  JOIN placement_drives d ON d.drive_id = a.drive_id
                  WHERE a.application_id = ? AND d.company_id = ?
                  """,
                  (application_id, company_id),
            ).fetchone()
      finally:
            recruita_db_connection.close()



def update_application_status_by_company(application_id, application_status):
      recruita_db_connection = connect_recruita_database()
      try:
            recruita_db_connection.execute(
                  "UPDATE applications SET application_status = ? WHERE application_id = ?",
                  (application_status, application_id),
            )
            recruita_db_connection.commit()
      finally:
            recruita_db_connection.close()
