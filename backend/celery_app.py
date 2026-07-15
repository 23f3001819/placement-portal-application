import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta
import csv
import io

celery_app = Celery(
    'placement_portal_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

celery_app.conf.timezone = 'UTC'

celery_app.conf.beat_schedule = {
    'daily-reminders-and-drive-completion': {
        'task': 'celery_app.send_daily_reminders',
        'schedule': crontab(hour=7, minute=30),
    },
    'monthly-placement-activity-report': {
        'task': 'celery_app.generate_monthly_report',
        'schedule': crontab(day_of_month=1, hour=7, minute=30),
    },
}

@celery_app.task
def send_daily_reminders():
    from app import app
    from controllers.database import db
    from controllers.models import Drive, Student, User, Appli, Company
    from mail import send_email

    with app.app_context():
        now = datetime.utcnow()
        
        drives_to_complete = Drive.query.filter(
            Drive.status == 1,
            Drive.deadline <= now
        ).all()
        
        completed_count = 0
        for drive in drives_to_complete:
            drive.status = 2
            completed_count += 1
            
        if completed_count > 0:
            db.session.commit()
            print(f"Daily Check: Set {completed_count} expired placement drives to Completed status.")

        upcoming_drives = Drive.query.filter(
            Drive.status == 1,
            Drive.deadline > now
        ).all()

        if not upcoming_drives:
            print("Daily Check: No upcoming drives to remind students about.")
            return

        students = Student.query.filter_by(status=0).all()
        
        for student in students:
            user = User.query.get(student.user_id)
            if not user or not user.email:
                continue

            reminder_drives = []
            for drive in upcoming_drives:
                cgpa_ok = student.cgpa >= drive.cgpa_c
                
                branches = drive.branch_c if isinstance(drive.branch_c, list) else []
                branch_ok = student.branch in branches or 'ALL' in branches
                
                if cgpa_ok and branch_ok:
                    applied = Appli.query.filter_by(stud_id=student.id, drive_id=drive.id).first()
                    if not applied:
                        company = Company.query.get(drive.comp_id)
                        comp_user = User.query.get(company.user_id) if company else None
                        comp_name = comp_user.name if comp_user else "Unknown Company"
                        reminder_drives.append({
                            'company_name': comp_name,
                            'job_role': drive.job_role,
                            'job_ctc': drive.job_ctc,
                            'deadline': drive.deadline.strftime('%Y-%m-%d %H:%M:%S')
                        })

            if reminder_drives:
                subject = "Daily Reminder: Upcoming Placement Drive Deadlines"
                
                body_html = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333333; line-height: 1.6; margin: 0; padding: 20px; background-color: #f8f9fa; }}
                        .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #eef2f5; }}
                        .header {{ border-bottom: 2px solid #007bff; padding-bottom: 15px; margin-bottom: 20px; }}
                        .header h2 {{ margin: 0; color: #007bff; font-weight: 600; }}
                        .intro {{ font-size: 16px; margin-bottom: 20px; }}
                        .drive-card {{ background-color: #fdfdfd; border: 1px solid #e2e8f0; border-left: 4px solid #007bff; border-radius: 4px; padding: 15px; margin-bottom: 15px; }}
                        .drive-title {{ font-size: 18px; font-weight: bold; color: #2d3748; margin: 0 0 5px 0; }}
                        .drive-company {{ font-size: 15px; color: #4a5568; margin: 0 0 10px 0; }}
                        .drive-meta {{ font-size: 13px; color: #718096; }}
                        .drive-meta strong {{ color: #4a5568; }}
                        .footer {{ margin-top: 30px; border-top: 1px solid #eef2f5; padding-top: 15px; font-size: 12px; color: #a0aec0; text-align: center; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>Upcoming Placement Drive Deadlines</h2>
                        </div>
                        <p class="intro">Hello <strong>{user.name}</strong>,</p>
                        <p class="intro">This is your daily reminder that you are eligible for the following active placement drives with upcoming application deadlines. Don't miss out on applying!</p>
                """
                
                for rd in reminder_drives:
                    body_html += f"""
                        <div class="drive-card">
                            <div class="drive-title">{rd['job_role']}</div>
                            <div class="drive-company">{rd['company_name']}</div>
                            <div class="drive-meta">
                                <strong>CTC:</strong> {rd['job_ctc']} LPA &nbsp;|&nbsp; 
                                <strong>Deadline:</strong> {rd['deadline']} UTC
                            </div>
                        </div>
                    """
                    
                body_html += """
                        <p class="intro" style="margin-top: 20px;">Please login to your Student Dashboard to submit your application.</p>
                        <div class="footer">
                            <p>This is an automated reminder from the Placement Portal.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                send_email(user.email, subject, body_html, is_html=True)
                print(f"Daily Check: Sent reminder to {user.email} with {len(reminder_drives)} upcoming drives.")

@celery_app.task
def generate_monthly_report():
    from app import app
    from controllers.models import Drive, Student, User, Appli, Company, Role
    from mail import send_email

    with app.app_context():
        today = datetime.utcnow().date()
        first_day_current_month = today.replace(day=1)

        last_day_prev_month = first_day_current_month - timedelta(days=1)
        first_day_prev_month = last_day_prev_month.replace(day=1)

        start_date = datetime(first_day_prev_month.year, first_day_prev_month.month, 1, 0, 0, 0)
        end_date = datetime(first_day_current_month.year, first_day_current_month.month, 1, 0, 0, 0)

        month_name = first_day_prev_month.strftime("%B %Y")

        drives_conducted = Drive.query.filter(
            Drive.deadline >= start_date,
            Drive.deadline < end_date
        ).all()
        drives_count = len(drives_conducted)

        applied_count = Appli.query.filter(
            Appli.applied_at >= start_date,
            Appli.applied_at < end_date
        ).count()

        selected_count = Appli.query.filter(
            Appli.status == 2,
            Appli.applied_at >= start_date,
            Appli.applied_at < end_date
        ).count()

        drives_details_html = ""
        if drives_conducted:
            drives_details_html += """
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Company Name</th>
                        <th>Job Role</th>
                        <th>CGPA Cutoff</th>
                        <th>CTC (LPA)</th>
                        <th>Deadline</th>
                    </tr>
                </thead>
                <tbody>
            """
            for drive in drives_conducted:
                company = Company.query.get(drive.comp_id)
                comp_user = User.query.get(company.user_id) if company else None
                comp_name = comp_user.name if comp_user else "Unknown"
                drives_details_html += f"""
                    <tr>
                        <td><strong>{comp_name}</strong></td>
                        <td>{drive.job_role}</td>
                        <td>{drive.cgpa_c}</td>
                        <td>{drive.job_ctc}</td>
                        <td>{drive.deadline.strftime('%Y-%m-%d %H:%M')}</td>
                    </tr>
                """
            drives_details_html += """
                </tbody>
            </table>
            """
        else:
            drives_details_html = "<p style='color: #718096; font-style: italic;'>No placement drives conducted in this period.</p>"

        admin_role = Role.query.filter_by(name='admin').first()
        admin_emails = []
        if admin_role:
            admins = User.query.filter(User.roles.contains(admin_role)).all()
            admin_emails = [admin.email for admin in admins if admin.email]
            
        if not admin_emails:
            admin_emails = ['admin@gmail.com']

        subject = f"Monthly Placement Activity Report - {month_name}"
        
        body_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333333; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f6f9; }}
                .container {{ max-width: 700px; margin: 0 auto; background-color: #ffffff; padding: 35px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #e1e8ed; }}
                .header {{ border-bottom: 3px solid #2b6cb0; padding-bottom: 15px; margin-bottom: 25px; }}
                .header h2 {{ margin: 0; color: #2b6cb0; font-size: 24px; font-weight: 700; }}
                .header p {{ margin: 5px 0 0 0; color: #718096; font-size: 14px; }}
                .stats-grid {{ display: flex; gap: 15px; margin-bottom: 30px; flex-wrap: wrap; }}
                .stat-card {{ flex: 1; min-width: 180px; background-color: #ebf8ff; border: 1px solid #bee3f8; border-radius: 6px; padding: 20px; text-align: center; }}
                .stat-value {{ font-size: 32px; font-weight: 800; margin-bottom: 5px; }}
                .stat-card.drives .stat-value {{ color: #2b6cb0; }}
                .stat-card.applied .stat-value {{ color: #b7791f; }}
                .stat-card.selected .stat-value {{ color: #22543d; }}
                .stat-label {{ font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; color: #4a5568; font-weight: 600; }}
                .section-title {{ font-size: 18px; font-weight: 600; color: #2d3748; margin-top: 30px; margin-bottom: 15px; border-left: 4px solid #2b6cb0; padding-left: 10px; }}
                .report-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }}
                .report-table th, .report-table td {{ border: 1px solid #e2e8f0; padding: 10px 12px; text-align: left; }}
                .report-table th {{ background-color: #edf2f7; color: #4a5568; font-weight: 600; }}
                .report-table tr:nth-child(even) {{ background-color: #f7fafc; }}
                .footer {{ margin-top: 40px; border-top: 1px solid #e2e8f0; padding-top: 15px; font-size: 12px; color: #a0aec0; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Monthly Placement Activity Report</h2>
                    <p>Report Period: {month_name}</p>
                </div>
                
                <p>Hello Admin,</p>
                <p>Here is the placement activity summary for the institute during the month of <strong>{month_name}</strong>.</p>
                
                <div class="stats-grid">
                    <div class="stat-card drives">
                        <div class="stat-value">{drives_count}</div>
                        <div class="stat-label">Drives Conducted</div>
                    </div>
                    <div class="stat-card applied">
                        <div class="stat-value">{applied_count}</div>
                        <div class="stat-label">Students Applied</div>
                    </div>
                    <div class="stat-card selected">
                        <div class="stat-value">{selected_count}</div>
                        <div class="stat-label">Students Selected</div>
                    </div>
                </div>
                
                <div class="section-title">Placement Drives with Deadlines in this Month</div>
                {drives_details_html}
                
                <div class="footer">
                    <p>Generated automatically by the Placement Portal System.</p>
                </div>
            </div>
        </body>
        </html>
        """

        for email in admin_emails:
            send_email(email, subject, body_html, is_html=True)
            print(f"Sent monthly report email to Admin: {email}")

@celery_app.task
def export_applications_csv(student_id):
    from app import app
    from controllers.models import Student, User, Appli, Drive, Company
    from mail import send_email

    with app.app_context():
        student = Student.query.get(student_id)
        if not student:
            print(f"Export CSV: Student with ID {student_id} not found.")
            return

        user = User.query.get(student.user_id)
        if not user or not user.email:
            print(f"Export CSV: User for student {student_id} not found or has no email.")
            return

        apps = Appli.query.filter_by(stud_id=student.id).all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Student ID', 'Company Name', 'Drive Title', 'Application Status', 'Dates'])

        status_map = {
            0: 'Applied',
            1: 'Shortlisted',
            2: 'Accepted / Placed',
            3: 'Rejected'
        }

        for app in apps:
            drive = Drive.query.get(app.drive_id)
            company_name = "Unknown"
            if drive:
                company = Company.query.get(drive.comp_id)
                if company:
                    comp_user = User.query.get(company.user_id)
                    if comp_user:
                        company_name = comp_user.name
            
            drive_title = drive.job_role if drive else "Unknown"
            app_status = status_map.get(app.status, f"Unknown ({app.status})")
            applied_date = app.applied_at.strftime('%Y-%m-%d %H:%M:%S') if app.applied_at else ""
            
            writer.writerow([student.id, company_name, drive_title, app_status, applied_date])

        csv_content = output.getvalue()
        output.close()

        subject = "Your Placement Application History Export"
        body = f"""Hello {user.name},

Please find attached your placement application history exported as a CSV file.

Summary of export:
Total applications: {len(apps)}

Best regards,
Placement Portal Team"""

        send_email(
            to_email=user.email,
            subject=subject,
            body=body,
            attachment_content=csv_content.encode('utf-8'),
            attachment_filename=f"application_history_{student.id}.csv"
        )
        print(f"Export CSV: Successfully exported and sent via email to {user.email}")
