from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_security import utils, auth_token_required , roles_required

from controllers.user_datastore import user_datastore
from controllers.database import db
from controllers.models import *

class LoginUser(Resource):
    def post(self):
        creds = request.get_json()
        if not creds or not creds['email'] or not creds['password']:
            return make_response(jsonify({'message': 'Email and password are required.'}), 400)
        user = user_datastore.find_user(email=creds['email'])
        if not user:
            return make_response(jsonify({'message': 'Cannot find user.'}), 404)
        if not utils.verify_password(creds['password'], user.password):
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
        creds = request.get_json(force=True)
        if not creds or not creds['name'] or not creds['email'] or not creds['password'] or not creds['role'] or not user_datastore.find_role(role=creds['role']):
            return make_response(jsonify({'message': 'Invalid input'}), 400)
        if user_datastore.find_user(email=creds['email']):
            return make_response(jsonify({'message': 'User already exists'}), 409)
        if creds['role'] == 'student':
            if not creds['role_data']['branch'] or not creds['role_data']['cgpa']:
                return make_response(jsonify({'message': 'Missing student profile details (name, branch, or cgpa).'}), 400)
        elif creds['role']== 'company':
            if not creds['role_data']['hr_con'] or not creds['role_data']['webs']:
                return make_response(jsonify({'message': 'Missing company profile details (name, hr_con, or webs).'}), 400)
        user_datastore.create_user(name=creds['name'], email=creds['email'], password=creds['password'], roles=[user_datastore.find_role(role=creds['role'])])
        db.session.flush()
        if creds['role'] == 'student':
            new_profile = Student(user_id = user_datastore.find_user(email=creds['email']).id,
                               branch = creds['role_data']['branch'],
                               cgpa = float(creds['role_data']['cgpa']))
            db.session.add(new_profile)
            result = {
                'message': 'Student registered successfully.',
                'user': {
                    'name': creds['name'],
                    'email': creds['email'],
                    'branch': new_profile.branch,
                    'cgpa': new_profile.cgpa
                }
            }
        if creds['role'] == 'company':
            new_profile = Company(user_id = user_datastore.find_user(email=creds['email']).id,
                               hr_con = creds['role_data']['hr_con'],
                               webs = creds['role_data']['webs'])
            db.session.add(new_profile)
            result = {
                'message': 'Company registered successfully.',
                'user': {
                    'name': creds['name'],
                    'email': creds['email'],
                    'hr_con': new_profile.hr_con,
                    'webs': new_profile.webs
                }
            }
        db.session.commit()
        
        return make_response(jsonify(result), 200)