from database import open_recruita_database


def fetch_student_profile(student_id):
    placement_db_connection = open_recruita_database()
    try:
        return placement_db_connection.execute(
            """
            SELECT student_id, full_name, roll_number, college, department,
                   gpa, resume, phone, email, is_active
            FROM students
            WHERE student_id = ?
            """,
            (student_id,),
        ).fetchone()
    finally:
        placement_db_connection.close()


def fetch_active_recruitment_drives(student_id, today_date):
    placement_db_connection = open_recruita_database()
    try:
        return placement_db_connection.execute(
            """
            SELECT d.drive_id, d.job_title, d.job_description, d.eligibility_criteria,
                   d.application_deadline, c.company_name,
                   CASE
                       WHEN EXISTS (
                           SELECT 1 FROM applications a
                           WHERE a.drive_id = d.drive_id AND a.student_id = ?
                       ) THEN 1 ELSE 0
                   END AS already_applied
            FROM placement_drives d
            JOIN companies c ON c.company_id = d.company_id
            WHERE d.drive_status = 'Approved'
              AND d.application_deadline >= ?
              AND c.approval_status = 'Approved'
              AND c.is_active = 1
            ORDER BY d.application_deadline ASC
            """,
            (student_id, today_date),
        ).fetchall()
    finally:
        placement_db_connection.close()


def fetch_drive_for_application(drive_id, today_date):
    placement_db_connection = open_recruita_database()
    try:
        return placement_db_connection.execute(
            """
            SELECT d.drive_id
            FROM placement_drives d
            JOIN companies c ON c.company_id = d.company_id
            WHERE d.drive_id = ?
              AND d.drive_status = 'Approved'
              AND d.application_deadline >= ?
              AND c.approval_status = 'Approved'
              AND c.is_active = 1
            """,
            (drive_id, today_date),
        ).fetchone()
    finally:
        placement_db_connection.close()


def fetch_existing_student_application(student_id, drive_id):
    placement_db_connection = open_recruita_database()
    try:
        return placement_db_connection.execute(
            "SELECT application_id FROM applications WHERE student_id = ? AND drive_id = ?",
            (student_id, drive_id),
        ).fetchone()
    finally:
        placement_db_connection.close()


def create_student_drive_application(student_id, drive_id, today_date):
    placement_db_connection = open_recruita_database()
    try:
        placement_db_connection.execute(
            """
            INSERT INTO applications(student_id, drive_id, application_date, application_status)
            VALUES (?, ?, ?, 'Applied')
            """,
            (student_id, drive_id, today_date),
        )
        placement_db_connection.commit()
    finally:
        placement_db_connection.close()


def fetch_student_application_history(student_id):
    placement_db_connection = open_recruita_database()
    try:
        return placement_db_connection.execute(
            """
            SELECT a.application_id, a.application_date, a.application_status,
                   d.job_title, c.company_name
            FROM applications a
            JOIN placement_drives d ON d.drive_id = a.drive_id
            JOIN companies c ON c.company_id = d.company_id
            WHERE a.student_id = ?
            ORDER BY a.application_id DESC
            """,
            (student_id,),
        ).fetchall()
    finally:
        placement_db_connection.close()


def update_student_profile(student_id, profile_data):
    placement_db_connection = open_recruita_database()
    try:
        placement_db_connection.execute(
            """
            UPDATE students
            SET full_name = ?, college = ?, department = ?, gpa = ?, resume = ?, phone = ?, email = ?
            WHERE student_id = ?
            """,
            (
                profile_data["full_name"],
                profile_data["college"],
                profile_data["department"],
                profile_data["gpa"],
                profile_data["resume"],
                profile_data["phone"],
                profile_data["email"],
                student_id,
            ),
        )
        placement_db_connection.commit()
    finally:
        placement_db_connection.close()
