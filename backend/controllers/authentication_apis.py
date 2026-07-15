import os
from werkzeug.utils import secure_filename

from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_security import utils, auth_token_required , roles_required

from controllers.user_datastore import user_datastore
from controllers.database import db
from controllers.models import *

class LoginUser(Resource):
    def post(self):
        creds = request.get_json()
        if not creds or not creds.get('email') or not creds.get('password'):
            return make_response(jsonify({'message': 'Email and password are required.'}), 400)
        user = user_datastore.find_user(email=creds.get('email'))
        if not user:
            return make_response(jsonify({'message': 'Cannot find user.'}), 404)
        if not utils.verify_password(creds.get('password'), user.password):
            return make_response(jsonify({'message': 'Invalid password.'}), 401)
        auth_token = user.get_auth_token()
        utils.login_user(user)
        result = {
            'message': 'Logged in successfully',
            'auth_token': auth_token,
            'user': {
                'email': user.email,
                'role': [r.name for r in user.roles]
            }
        }
        return make_response(jsonify(result), 200)

class LogoutUser(Resource):
    @auth_token_required
    def post(self):
        utils.logout_user()
        return make_response(jsonify({'message': 'Logout successful.'}), 200)

class RegisterUser(Resource):
    def post(self):
        creds = request.form
        if not creds or not creds.get('name') or not creds.get('email') or not creds.get('password') or not creds.get('role') or not user_datastore.find_role(role=creds.get('role')):
            return make_response(jsonify({'message': 'Invalid input'}), 400)
        if user_datastore.find_user(email=creds.get('email')):
            return make_response(jsonify({'message': 'User already exists'}), 409)
        if creds.get('role') == 'student':
            if not creds.get('branch') or not creds.get('cgpa'):
                return make_response(jsonify({'message': 'Missing student profile details (name, branch, or cgpa).'}), 400)
        elif creds.get('role') == 'company':
            if not creds.get('hr_con') or not creds.get('webs'):
                return make_response(jsonify({'message': 'Missing company profile details (name, hr_con, or webs).'}), 400)
        
        user_datastore.create_user(name=creds.get('name'), email=creds.get('email'), password=creds.get('password'), roles=[user_datastore.find_role(role=creds.get('role'))])
        db.session.flush()
        
        if creds.get('role') == 'student':
            resume_path_db = None
            if 'resume' in request.files:
                file = request.files['resume']
                if file and file.filename.endswith('.pdf'):
                    new_user_id = user_datastore.find_user(email=creds.get('email')).id
                    filename = secure_filename(f"student_{new_user_id}_{file.filename}")
                    
                    os.makedirs('static/resumes', exist_ok=True)
                    file_path = os.path.join('static/resumes', filename)
                    file.save(file_path)
                    
                    resume_path_db = f"static/resumes/{filename}"

            new_profile = Student(user_id = user_datastore.find_user(email=creds.get('email')).id,
                               branch = creds.get('branch'),
                               cgpa = float(creds.get('cgpa')),
                               resume_path = resume_path_db)
                               
            db.session.add(new_profile)
            result = {
                'message': 'Student registered successfully.',
                'user': {
                    'name': creds.get('name'),
                    'email': creds.get('email'),
                    'branch': new_profile.branch,
                    'cgpa': new_profile.cgpa,
                    'resume': new_profile.resume_path
                }
            }
        
        if creds.get('role') == 'company':
            new_profile = Company(user_id = user_datastore.find_user(email=creds.get('email')).id,
                               hr_con = creds.get('hr_con'),
                               webs = creds.get('webs'))
            db.session.add(new_profile)
            result = {
                'message': 'Company registered successfully.',
                'user': {
                    'name': creds.get('name'),
                    'email': creds.get('email'),
                    'hr_con': new_profile.hr_con,
                    'webs': new_profile.webs
                }
            }
        db.session.commit()
        
        return make_response(jsonify(result), 200)