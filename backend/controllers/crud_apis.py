import os
from werkzeug.utils import secure_filename
from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_security import utils, auth_token_required, roles_required, current_user

from controllers.database import db
from controllers.models import *

from controllers.user_datastore import user_datastore 

from datetime import datetime
from sqlalchemy import or_





class AdminStatsAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self):
        student_count = Student.query.count()
        company_count = Company.query.count()
        drive_count = Drive.query.count()
        
        return make_response(jsonify({
            'total_students': student_count,
            'total_companies': company_count,
            'total_drives': drive_count
        }), 200)


class AdminManageCompanyAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self):
        search_query = request.args.get('search', '').lower()
        if search_query:
            users = User.query.filter(User.roles.any(name='company'), User.name.ilike(f"%{search_query}%")).all()
            user_ids = [u.id for u in users]
            companies = Company.query.filter(Company.user_id.in_(user_ids)).all()
        else:
            companies = Company.query.all()
            
        result = []
        for comp in companies:
            user = User.query.get(comp.user_id)
            result.append({
                'comp_id': comp.id,
                'name': user.name,
                'email': user.email,
                'hr_con': comp.hr_con,
                'status': comp.status
            })
        return make_response(jsonify(result), 200)

    @auth_token_required
    @roles_required('admin')
    def put(self, comp_id):
        data = request.get_json()
        comp = Company.query.get(comp_id)
        if not comp:
            return make_response(jsonify({'message': 'Company not found'}), 404)
        
        comp.status = data.get('status', comp.status)
        db.session.commit()
        return make_response(jsonify({'message': 'Company status updated.'}), 200)

    @auth_token_required
    @roles_required('admin')
    def delete(self, comp_id):
        comp = Company.query.get(comp_id)
        if not comp:
            return make_response(jsonify({'message': 'Company not found'}), 404)
         
        user = User.query.get(comp.user_id)
        user_datastore.delete_user(user) 
        db.session.commit()
        
        return make_response(jsonify({'message': 'Company and all associated data permanently deleted.'}), 200)


class AdminManageStudentAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self):
        search_query = request.args.get('search', '').lower()
        if search_query:
            users = User.query.filter(User.roles.any(name='student'), User.name.ilike(f"%{search_query}%")).all()
            user_ids = [u.id for u in users]
            students = Student.query.filter(Student.user_id.in_(user_ids)).all()
        else:
            students = Student.query.all()
            
        result = []
        for stud in students:
            user = User.query.get(stud.user_id)
            result.append({
                'stud_id': stud.id,
                'name': user.name,
                'branch': stud.branch,
                'cgpa': stud.cgpa,
                'status': stud.status 
            })
        return make_response(jsonify(result), 200)

    @auth_token_required
    @roles_required('admin')
    def put(self, stud_id):
        data = request.get_json()
        stud = Student.query.get(stud_id)
        if not stud:
            return make_response(jsonify({'message': 'Student not found'}), 404)
            
        new_status = data.get('status', stud.status)
        if stud.status == 2 and new_status == 0:
            has_accepted = Appli.query.filter_by(stud_id=stud.id, status=2).first()
            if has_accepted:
                new_status = 1
        
        stud.status = new_status
        db.session.commit()
        return make_response(jsonify({'message': 'Student status updated.'}), 200)

    @auth_token_required
    @roles_required('admin')
    def delete(self, stud_id):
        stud = Student.query.get(stud_id)
        if not stud:
            return make_response(jsonify({'message': 'Student not found'}), 404)
            
        
        user = User.query.get(stud.user_id)
        user_datastore.delete_user(user)
        db.session.commit()
        
        return make_response(jsonify({'message': 'Student and applications permanently deleted.'}), 200)


class AdminManageDriveAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def put(self, drive_id):
        data = request.get_json()
        drive = Drive.query.get(drive_id)
        if not drive:
            return make_response(jsonify({'message': 'Drive not found'}), 404)
            
        drive.status = data.get('status', drive.status)
        db.session.commit()
        return make_response(jsonify({'message': 'Drive status updated.'}), 200)

    @auth_token_required
    @roles_required('admin')
    def delete(self, drive_id):
        drive = Drive.query.get(drive_id)
        if not drive:
            return make_response(jsonify({'message': 'Drive not found'}), 404)
            
        
        db.session.delete(drive)
        db.session.commit()
        return make_response(jsonify({'message': 'Placement drive deleted successfully.'}), 200)






class DriveListAPI(Resource):
    @auth_token_required
    @roles_required('company')
    def post(self):
        data = request.get_json()
        comp_id = data.get('comp_id')
        
        if comp_id:
            company = Company.query.get(comp_id)
            if not company or company.user_id != current_user.id:
                return make_response(jsonify({'message': 'Unauthorized or Invalid Company ID.'}), 403)
        else:
            company = Company.query.filter_by(user_id=current_user.id).first()
            if not company:
                return make_response(jsonify({'message': 'Company profile not found.'}), 404)
        
        if company.status == 0:
            return make_response(jsonify({'message': 'Your account is blacklisted. Contact Admin.'}), 403)
            
        branch_c_data = data['branch_c']
        if isinstance(branch_c_data, str):
            branch_c_data = [b.strip() for b in branch_c_data.split(',')]
            
        new_drive = Drive(
            comp_id = company.id,
            cgpa_c = float(data['cgpa_c']),
            branch_c = branch_c_data,
            job_role = data['job_role'],
            job_desc = data.get('job_desc', ""),
            job_ctc = float(data['job_ctc']),
            deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00')),
            status = 0 
        )
        db.session.add(new_drive)
        db.session.commit()
        return make_response(jsonify({'message': 'New drive created. Pending admin approval.'}), 201)
    
    def get(self):
        drive_objs = Drive.query.all()
        result = []
        for d in drive_objs:
            company = Company.query.get(d.comp_id)
            comp_name = "Unknown Company"
            if company:
                user = User.query.get(company.user_id)
                if user:
                    comp_name = user.name
            result.append({
                'id': d.id,
                'comp_id': d.comp_id,
                'company_name': comp_name,
                'cgpa_c': d.cgpa_c,
                'branch_c': d.branch_c,
                'job_role': d.job_role,
                'job_desc': d.job_desc,
                'job_ctc': d.job_ctc,
                'job_pay': d.job_ctc,
                'deadline': d.deadline.isoformat(),
                'status': d.status
            })
        return make_response(jsonify(result), 200)

class GetCompDrive(Resource):
    def get(self, co_id=None):
        drive_objs = Drive.query.filter_by(comp_id = co_id).all()
        result = [{
            'id': d.id,
            'comp_id': d.comp_id,
            'cgpa_c': d.cgpa_c,
            'branch_c': d.branch_c,
            'job_role': d.job_role,
            'job_desc': d.job_desc,
            'job_ctc': d.job_ctc,
            'job_pay': d.job_ctc,
            'deadline': d.deadline.isoformat(),
            'status': d.status
        } for d in drive_objs]
        return make_response(jsonify(result), 200)

class SingleDriveAPI(Resource):
    @auth_token_required
    @roles_required('company')
    def get(self, drive_id):
        drive_obj = Drive.query.filter_by(id=drive_id).first()
        if not drive_obj:
            return make_response(jsonify({'message': 'Drive not found.'}), 404)
        
        company = Company.query.filter_by(user_id=current_user.id).first()
        if not company or drive_obj.comp_id != company.id:
            return make_response(jsonify({'message': 'Unauthorized or Invalid ID.'}), 403)
            
        result = {
            'id': drive_obj.id,
            'comp_id': drive_obj.comp_id,
            'cgpa_c': drive_obj.cgpa_c,
            'branch_c': drive_obj.branch_c,
            'job_role': drive_obj.job_role,
            'job_desc': drive_obj.job_desc,
            'job_ctc': drive_obj.job_ctc,
            'deadline': drive_obj.deadline.isoformat(),
            'status': drive_obj.status
        }
        return make_response(jsonify(result), 200)

    @auth_token_required
    @roles_required('company')
    def put(self, drive_id):
        drive_obj = Drive.query.filter_by(id=drive_id).first()
        if not drive_obj or drive_obj.comp_id != Company.query.filter_by(user_id=current_user.id).first().id:
            return make_response(jsonify({'message': 'Unauthorized or Invalid ID.'}), 403)
            
        data = request.get_json()
        
        if data.get('cgpa_c') is not None: drive_obj.cgpa_c = float(data['cgpa_c'])
        if data.get('branch_c'):
            branch_c_data = data['branch_c']
            if isinstance(branch_c_data, str):
                branch_c_data = [b.strip() for b in branch_c_data.split(',')]
            drive_obj.branch_c = branch_c_data
        if data.get('job_role'): drive_obj.job_role = data['job_role']
        if data.get('job_desc') is not None: drive_obj.job_desc = data['job_desc']
        if data.get('job_ctc') is not None: drive_obj.job_ctc = float(data['job_ctc'])
        if data.get('deadline'): drive_obj.deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
        
        new_status = data.get('status')
        if new_status is not None:
            if new_status in [1, 2] and drive_obj.status == 0:
                return make_response(jsonify({'message': 'Cannot alter pending drive.'}), 403)
            if new_status == 2 and drive_obj.status == 1:
                drive_obj.status = 2
                drive_obj.deadline = datetime.utcnow()
            elif new_status == 1 and drive_obj.status == 2:
                if drive_obj.deadline > datetime.utcnow():
                    drive_obj.status = 1
                else:
                    return make_response(jsonify({'message': 'Future deadline required.'}), 400)

        db.session.commit()
        return make_response(jsonify({'message': 'Drive updated.'}), 200)

    @auth_token_required
    @roles_required('company')
    def delete(self, drive_id):
        drive_obj = Drive.query.filter_by(id=drive_id).first()
        if not drive_obj or drive_obj.comp_id != Company.query.filter_by(user_id=current_user.id).first().id:
            return make_response(jsonify({'message': 'Unauthorized or Invalid ID.'}), 403)
            
        if drive_obj.status != 0:
            return make_response(jsonify({'message': 'Can only delete pending drives. For active drives, please end them.'}), 403)
            
        db.session.delete(drive_obj)
        db.session.commit()
        
        return make_response(jsonify({'message': 'Pending drive withdrawn successfully.'}), 200)






class StudentProfileAPI(Resource):
    @auth_token_required
    @roles_required('student')
    def get(self):
        student = Student.query.filter_by(user_id=current_user.id).first()
        return make_response(jsonify({
            'name': current_user.name,
            'email': current_user.email,
            'branch': student.branch,
            'cgpa': student.cgpa,
            'resume_path': student.resume_path,
            'status': student.status
        }), 200)

    @auth_token_required
    @roles_required('student')
    def put(self):
        student = Student.query.filter_by(user_id=current_user.id).first()
        form_data = request.form
        
                                                 
        new_email = form_data.get('email')
        if new_email and new_email != current_user.email:
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user:
                return make_response(jsonify({'message': 'Email is already taken by another user.'}), 400)
            current_user.email = new_email
            
        if form_data.get('name'):
            current_user.name = form_data.get('name')
            
        if form_data.get('password'):
            current_user.password = form_data.get('password')
            
        if form_data.get('branch'): student.branch = form_data.get('branch')
        if form_data.get('cgpa'): student.cgpa = float(form_data.get('cgpa'))
        
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename.endswith('.pdf'):
                filename = secure_filename(f"student_{current_user.id}_{file.filename}")
                os.makedirs('static/resumes', exist_ok=True)
                file_path = os.path.join('static/resumes', filename)
                file.save(file_path)
                student.resume_path = f"static/resumes/{filename}"
                
        db.session.commit()
        return make_response(jsonify({
            'message': 'Profile updated successfully.',
            'user': {
                'name': current_user.name,
                'email': current_user.email
            }
        }), 200)


class StudentEligibleDrivesAPI(Resource):
    @auth_token_required
    @roles_required('student')
    def get(self):
        student = Student.query.filter_by(user_id=current_user.id).first()
        
        active_drives = Drive.query.filter(
            Drive.status == 1,
            Drive.cgpa_c <= student.cgpa,
            Drive.deadline > datetime.utcnow()
        ).all()
        
        eligible_drives = []
        for d in active_drives:
            if student.branch in d.branch_c or "ALL" in d.branch_c:
                comp_user = User.query.get(Company.query.get(d.comp_id).user_id)
                eligible_drives.append({
                    'id': d.id,
                    'company_name': comp_user.name,
                    'job_role': d.job_role,
                    'job_ctc': d.job_ctc,
                    'deadline': d.deadline.isoformat()
                })
                
        return make_response(jsonify(eligible_drives), 200)






class ApplicationAPI(Resource):
    @auth_token_required
    @roles_required('student')
    def post(self, drive_id):
        student = Student.query.filter_by(user_id=current_user.id).first()
        
        if student.status == 1:
            return make_response(jsonify({'message': 'You are already placed and cannot apply.'}), 403)
        if student.status == 2:
            return make_response(jsonify({'message': 'You have been blacklisted.'}), 403)
            
        drive = Drive.query.get(drive_id)
        if not drive or drive.status != 1 or drive.deadline < datetime.utcnow():
            return make_response(jsonify({'message': 'Drive is not active or deadline passed.'}), 400)
            
        existing_app = Appli.query.filter_by(stud_id=student.id, drive_id=drive_id).first()
        if existing_app:
            return make_response(jsonify({'message': 'Already applied to this drive.'}), 409)
            
        new_app = Appli(
            drive_id=drive_id,
            stud_id=student.id,
            applied_at=datetime.utcnow(),
            status=0 
        )
        db.session.add(new_app)
        db.session.commit()
        return make_response(jsonify({'message': 'Application successful.'}), 201)

    @auth_token_required
    def get(self, drive_id=None):
        if 'admin' in [r.name for r in current_user.roles]:
            apps = Appli.query.all()
            result = []
            for app in apps:
                drive = Drive.query.get(app.drive_id)
                stud = Student.query.get(app.stud_id)
                if not drive or not stud:
                    continue
                company = Company.query.get(drive.comp_id)
                comp_user = User.query.get(company.user_id) if company else None
                stud_user = User.query.get(stud.user_id) if stud else None
                result.append({
                    'app_id': app.id,
                    'student_name': stud_user.name if stud_user else 'Unknown Student',
                    'student_email': stud_user.email if stud_user else '',
                    'company': comp_user.name if comp_user else 'Unknown Company',
                    'job_role': drive.job_role,
                    'status': app.status,
                    'applied_at': app.applied_at.isoformat()
                })
            return make_response(jsonify(result), 200)

        elif 'student' in [r.name for r in current_user.roles]:
            student = Student.query.filter_by(user_id=current_user.id).first()
            apps = Appli.query.filter_by(stud_id=student.id).all()
            result = []
            for app in apps:
                drive = Drive.query.get(app.drive_id)
                comp = User.query.get(Company.query.get(drive.comp_id).user_id)
                result.append({
                    'app_id': app.id,
                    'company': comp.name,
                    'job_role': drive.job_role,
                    'status': app.status, 
                    'applied_at': app.applied_at.isoformat()
                })
            return make_response(jsonify(result), 200)
            
                               
        elif 'company' in [r.name for r in current_user.roles] and drive_id:
            company = Company.query.filter_by(user_id=current_user.id).first()
            drive = Drive.query.filter_by(id=drive_id, comp_id=company.id).first()
            if not drive:
                return make_response(jsonify({'message': 'Unauthorized'}), 403)
                
            apps = Appli.query.filter_by(drive_id=drive.id).all()
            result = []
            for app in apps:
                stud = Student.query.get(app.stud_id)
                user = User.query.get(stud.user_id)
                result.append({
                    'app_id': app.id,
                    'student_name': user.name,
                    'branch': stud.branch,
                    'cgpa': stud.cgpa,
                    'resume_path': stud.resume_path,
                    'status': app.status
                })
            return make_response(jsonify(result), 200)
            
        return make_response(jsonify({'message': 'Bad Request'}), 400)

    @auth_token_required
    @roles_required('student')
    def delete(self, drive_id):
        student = Student.query.filter_by(user_id=current_user.id).first()
        appli = Appli.query.filter_by(stud_id=student.id, drive_id=drive_id).first()
        
        if not appli:
            return make_response(jsonify({'message': 'Application not found.'}), 404)
            
        
        if appli.status != 0:
            return make_response(jsonify({'message': 'Cannot withdraw application once processed by the company.'}), 403)
            
        db.session.delete(appli)
        db.session.commit()
        return make_response(jsonify({'message': 'Application withdrawn successfully.'}), 200)


class ManageApplicationAPI(Resource):
    @auth_token_required
    @roles_required('company')
    def put(self, app_id):
        company = Company.query.filter_by(user_id=current_user.id).first()
        appli = Appli.query.get(app_id)
        
        if not appli:
            return make_response(jsonify({'message': 'Application not found'}), 404)
            
        drive = Drive.query.get(appli.drive_id)
        if drive.comp_id != company.id:
            return make_response(jsonify({'message': 'Unauthorized'}), 403)
            
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status is not None:
            appli.status = new_status
            
            student = Student.query.get(appli.stud_id)
            if student:
                if new_status == 2:
                    student.status = 1
                else:
                                                                             
                    other_accepted = Appli.query.filter(
                        Appli.stud_id == student.id,
                        Appli.id != appli.id,
                        Appli.status == 2
                    ).first()
                    if not other_accepted:
                        student.status = 0
                
        db.session.commit()
        return make_response(jsonify({'message': 'Application status updated.'}), 200)
    
class CompDetails(Resource):
    def post(self):
        det = request.get_json() or {}
        email = det.get('email')
        if not email:
            return make_response(jsonify({'message': 'Email is required'}), 400)

        user = User.query.filter_by(email=email).first()
        if not user:
            return make_response(jsonify({'message': 'No company found'}), 404)

        comp_user = Company.query.filter_by(user_id=user.id).first()
        if not comp_user:
            return make_response(jsonify({'message': 'No company found'}), 404)
        if comp_user.status == 0:
            return make_response(jsonify({'message': 'Company is blacklisted. Contact admin.'}), 404)
        result = {
            'message': 'Company details',
            'id': comp_user.id,
            'user_id': comp_user.user_id,
            'hr_con': comp_user.hr_con,
            'webs': comp_user.webs,
            'status': comp_user.status
        }
        return make_response(jsonify(result), 200)

class CompanyProfileAPI(Resource):
    @auth_token_required
    @roles_required('company')
    def get(self):
        company = Company.query.filter_by(user_id=current_user.id).first()
        if not company:
            return make_response(jsonify({'message': 'Company profile not found.'}), 404)
        return make_response(jsonify({
            'name': current_user.name,
            'email': current_user.email,
            'hr_con': company.hr_con,
            'webs': company.webs,
            'status': company.status
        }), 200)

    @auth_token_required
    @roles_required('company')
    def put(self):
        company = Company.query.filter_by(user_id=current_user.id).first()
        if not company:
            return make_response(jsonify({'message': 'Company profile not found.'}), 404)
            
        data = request.get_json()
        if not data:
            return make_response(jsonify({'message': 'Invalid data.'}), 400)
            
        new_email = data.get('email')
        if new_email and new_email != current_user.email:
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user:
                return make_response(jsonify({'message': 'Email is already taken by another user.'}), 400)
            current_user.email = new_email
            
        if data.get('name'):
            current_user.name = data.get('name')
            
        if data.get('password'):
            current_user.password = data.get('password')
            
        if data.get('hr_con'):
            existing_hr = Company.query.filter(Company.hr_con == data.get('hr_con'), Company.id != company.id).first()
            if existing_hr:
                return make_response(jsonify({'message': 'HR Contact already registered by another company.'}), 400)
            company.hr_con = data.get('hr_con')
            
        if data.get('webs'):
            existing_webs = Company.query.filter(Company.webs == data.get('webs'), Company.id != company.id).first()
            if existing_webs:
                return make_response(jsonify({'message': 'Website already registered by another company.'}), 400)
            company.webs = data.get('webs')
            
        db.session.commit()
        return make_response(jsonify({
            'message': 'Profile updated successfully.',
            'user': {
                'name': current_user.name,
                'email': current_user.email
            }
        }), 200)

class AdminProfileAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self):
        return make_response(jsonify({
            'name': current_user.name,
            'email': current_user.email
        }), 200)

    @auth_token_required
    @roles_required('admin')
    def put(self):
        data = request.get_json()
        if not data:
            return make_response(jsonify({'message': 'Invalid data.'}), 400)
            
        new_email = data.get('email')
        if new_email and new_email != current_user.email:
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user:
                return make_response(jsonify({'message': 'Email is already taken by another user.'}), 400)
            current_user.email = new_email
            
        if data.get('name'):
            current_user.name = data.get('name')
            
        if data.get('password'):
            current_user.password = data.get('password')
            
        db.session.commit()
        return make_response(jsonify({
            'message': 'Profile updated successfully.',
            'user': {
                'name': current_user.name,
                'email': current_user.email
            }
        }), 200)

class StudentExportApplicationsAPI(Resource):
    @auth_token_required
    @roles_required('student')
    def post(self):
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            return make_response(jsonify({'message': 'Student profile not found.'}), 404)
        
                                            
        from celery_app import export_applications_csv
        export_applications_csv.delay(student.id)
        
        return make_response(jsonify({'message': 'Export started. You will receive the CSV file via email shortly.'}), 200)