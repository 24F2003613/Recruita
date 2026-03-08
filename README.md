# Recruita - Placement Portal

Recruita is a Flask + SQLite based placement portal with three roles:
- Admin (predefined placement cell user)
- Company (requires admin approval)
- Student (no approval)

## Setup and Run

1. Open terminal in project folder:
   ```bash
   cd Recruita
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python3 app.py
   ```

5. Open in browser:
   - `http://127.0.0.1:5000`

## Default Admin Login
On first run, tables are created programmatically and one admin account is inserted.

- Email: `placement.officer@iitm.ac.in`
- Password: `Recruita@123`