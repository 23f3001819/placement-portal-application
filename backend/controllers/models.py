from controllers.database import db
from flask_security import UserMixin, RoleMixin
from sqlalchemy import JSON, DateTime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)

    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    fs_token_uniquifier = db.Column(db.String(255), unique=True, nullable=True)

    roles = db.relationship('Role', secondary='user_roles')

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

class UserRoles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hr_con = db.Column(db.String(10), unique=True, nullable=False)
    webs = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.Integer, default=1, nullable=False)

    drives = db.relationship('Drive', backref='company', lazy=True)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    branch = db.Column(db.String(255), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    status = db.Column(db.Integer, default=0, nullable=False)

    applications = db.relationship('Appli', backref='student', lazy=True)

class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comp_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    cgpa_c = db.Column(db.Float, default=5, nullable=False)
    branch_c = db.Column(JSON, nullable=False)
    job_role = db.Column(db.String(255), nullable=False)
    job_desc = db.Column(db.String)
    job_ctc = db.Column(db.Float, nullable=False)
    deadline = db.Column(DateTime, nullable=False)
    status = db.Column(db.Integer, default=0, nullable=False)

    applications = db.relationship('Appli', backref='drive', lazy=True)

class Appli(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'))
    stud_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    applied_at = db.Column(DateTime, nullable=False)
    status = db.Column(db.Integer, default=0, nullable=False)
    