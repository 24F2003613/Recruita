import sqlite3
DATABASE_PATH = "recruita_portal.db"

def connect_recruita_database():
      recruita_db_connection = sqlite3.connect(DATABASE_PATH)
      recruita_db_connection.row_factory = sqlite3.Row
      recruita_db_connection.execute("PRAGMA foreign_keys = ON")
      return recruita_db_connection


def create_recruita_core_tables():
      recruita_db_connection = connect_recruita_database()
      try:
            recruita_db_connection.executescript(
                  """
                  CREATE TABLE IF NOT EXISTS admins (
                        admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL
                  );


                  CREATE TABLE IF NOT EXISTS students (
                        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        full_name TEXT NOT NULL,
                        roll_number TEXT NOT NULL UNIQUE,
                        college TEXT NOT NULL DEFAULT '',
                        department TEXT NOT NULL,
                        gpa TEXT NOT NULL DEFAULT '',
                        resume TEXT NOT NULL DEFAULT '',
                        phone TEXT,
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        is_active INTEGER NOT NULL DEFAULT 1
                  );


                  CREATE TABLE IF NOT EXISTS companies (
                        company_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_name TEXT NOT NULL,
                        website TEXT NOT NULL DEFAULT '',
                        hr_name TEXT NOT NULL,
                        phone TEXT NOT NULL DEFAULT '',
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL DEFAULT '',
                        approval_status TEXT NOT NULL DEFAULT 'Pending'
                              CHECK(approval_status IN ('Pending', 'Approved', 'Rejected')),
                        is_active INTEGER NOT NULL DEFAULT 1
                  );


                  CREATE TABLE IF NOT EXISTS placement_drives (
                        drive_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_id INTEGER NOT NULL,
                        job_title TEXT NOT NULL,
                        job_description TEXT NOT NULL,
                        eligibility_criteria TEXT NOT NULL,
                        application_deadline TEXT NOT NULL,
                        drive_status TEXT NOT NULL DEFAULT 'Pending'
                              CHECK(drive_status IN ('Pending', 'Approved', 'Closed')),
                        FOREIGN KEY (company_id) REFERENCES companies(company_id)
                  );


                  CREATE TABLE IF NOT EXISTS applications (
                        application_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER NOT NULL,
                        drive_id INTEGER NOT NULL,
                        application_date TEXT NOT NULL,
                        application_status TEXT NOT NULL DEFAULT 'Applied'
                              CHECK(application_status IN ('Applied', 'Shortlisted', 'Selected', 'Rejected')),
                        UNIQUE(student_id, drive_id),
                        FOREIGN KEY (student_id) REFERENCES students(student_id),
                        FOREIGN KEY (drive_id) REFERENCES placement_drives(drive_id)
                  );
                  """
            )


            existing_admin_account = recruita_db_connection.execute(
                  "SELECT admin_id FROM admins ORDER BY admin_id LIMIT 1"
            ).fetchone()


            # Admin is a pre-existing placement cell account.
            if not existing_admin_account:
                  recruita_db_connection.execute(
                        """
                        INSERT INTO admins(name, email, password)
                        VALUES (?, ?, ?)
                        """,
                        ("Placement Officer", "placement.officer@iitm.ac.in", "Recruita@123"),
                  )


            recruita_db_connection.commit()
      finally:
            recruita_db_connection.close()
