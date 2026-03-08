from flask import abort, flash, redirect, render_template, request, session, url_for


from models.admin_models import (
      fetch_admin_profile,
      fetch_admin_dashboard_counts,
      fetch_all_applications_for_admin_panel,
      fetch_all_drives_for_admin_panel,
      fetch_companies_pending_approval,
      fetch_drives_pending_approval,
      search_companies_for_admin_panel,
      search_students_for_admin_panel,
      toggle_company_account_active_state,
      toggle_student_account_active_state,
      update_company_approval_status,
      update_drive_status,
)
from models.auth_models import require_admin_role



def register_admin_routes(app):
      @app.route("/admin/profile")
      @require_admin_role
      def admin_profile():
            admin_id = session.get("role_id")
            if not admin_id:
                  abort(403)


            admin_profile_data = fetch_admin_profile(admin_id)
            if not admin_profile_data:
                  abort(403)


            return render_template("admin/admin_profile.html", admin_profile_data=admin_profile_data)


      @app.route("/admin/dashboard")
      @require_admin_role
      def admin_dashboard():
            return render_template(
                  "admin/admin_dashboard.html",
                  dashboard_totals=fetch_admin_dashboard_counts(),
                  companies_pending_clearance=fetch_companies_pending_approval(),
                  drives_waiting_clearance=fetch_drives_pending_approval(),
            )


      @app.route("/admin/approve-company/<int:company_id>", methods=["POST"])
      @require_admin_role
      def approve_company(company_id):
            approval_decision = request.form.get("approval_decision", "Approved")
            if approval_decision not in {"Approved", "Rejected"}:
                  return "Invalid company approval decision", 400


            try:
                  update_company_approval_status(company_id, approval_decision)
            except Exception as db_error:
                  print("Error while updating company approval status:", db_error)
            return redirect(url_for("admin_dashboard"))


      @app.route("/admin/approve-drive/<int:drive_id>", methods=["POST"])
      @require_admin_role
      def approve_drive(drive_id):
            try:
                  update_drive_status(drive_id, "Approved")
            except Exception as db_error:
                  print("Error while approving placement drive:", db_error)
            return redirect(url_for("admin_dashboard"))


      @app.route("/admin/reject-drive/<int:drive_id>", methods=["POST"])
      @require_admin_role
      def reject_drive(drive_id):
            try:
                  update_drive_status(drive_id, "Closed")
            except Exception as db_error:
                  print("Error while rejecting placement drive:", db_error)
            return redirect(url_for("admin_dashboard"))


      @app.route("/admin/students")
      @require_admin_role
      def admin_students():
            student_search_query = request.args.get("q", "").strip()
            return render_template(
                  "admin/admin_students.html",
                  student_search_query=student_search_query,
                  students_waiting_for_review=search_students_for_admin_panel(student_search_query),
            )


      @app.route("/admin/toggle-student-active/<int:student_id>", methods=["POST"])
      @require_admin_role
      def toggle_student_active(student_id):
            try:
                  toggle_student_account_active_state(student_id)
            except Exception as db_error:
                  print("Error while updating student active status:", db_error)
            return redirect(url_for("admin_students"))


      @app.route("/admin/companies")
      @require_admin_role
      def admin_companies():
            company_search_query = request.args.get("q", "").strip()
            return render_template(
                  "admin/admin_companies.html",
                  company_search_query=company_search_query,
                  registered_companies=search_companies_for_admin_panel(company_search_query),
            )


      @app.route("/admin/toggle-company-active/<int:company_id>", methods=["POST"])
      @require_admin_role
      def toggle_company_active(company_id):
            try:
                  company_account_state_change = toggle_company_account_active_state(company_id)
                  if company_account_state_change == "reactivated_pending":
                        flash("Company activated and moved to Pending for re-approval.", "warning")
                  elif company_account_state_change == "blacklisted":
                        flash("Company has been deactivated and marked as blacklisted.", "warning")
            except Exception as db_error:
                  print("Error while updating company active status:", db_error)
            return redirect(url_for("admin_companies"))


      @app.route("/admin/update-company-approval/<int:company_id>", methods=["POST"])
      @require_admin_role
      def update_company_approval(company_id):
            approval_decision = request.form.get("approval_status", "").strip()
            if approval_decision not in {"Pending", "Approved", "Rejected"}:
                  return "Invalid approval status", 400
            try:
                  update_company_approval_status(company_id, approval_decision)
            except Exception as db_error:
                  print("Error while updating company approval:", db_error)
            return redirect(url_for("admin_companies"))


      @app.route("/admin/drives")
      @require_admin_role
      def admin_drives():
            return render_template(
                  "admin/admin_drives.html",
                  all_placement_drives=fetch_all_drives_for_admin_panel(),
            )


      @app.route("/admin/applications")
      @require_admin_role
      def admin_applications():
            return render_template(
                  "admin/admin_applications.html",
                  all_student_applications=fetch_all_applications_for_admin_panel(),
            )
