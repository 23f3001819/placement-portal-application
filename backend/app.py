from flask import Flask
from flask_security import Security
from flask_restful import Api
from flask_cors import CORS

from controllers.database import db
from controllers.config import Config
from controllers.user_datastore import user_datastore

from controllers.authentication_apis import LoginUser, LogoutUser, RegisterUser

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    security = Security(app, user_datastore)
    api = Api(app, prefix='/api')

    with app.app_context():
        db.create_all()

        admin_role = user_datastore.find_or_create_role(name='admin', description='Administrator')
        student_role = user_datastore.find_or_create_role(name='student', description='Student User')
        company_role = user_datastore.find_or_create_role(name='company', description='Company User')

        if not user_datastore.find_user(email='admin@gmail.com'):
            user_datastore.create_user(
                name="Admin",
                email="admin@gmail.com",
                password="admin123",
                roles=[admin_role] 
            )
        db.session.commit()

    return app, api

app, api = create_app()

CORS(app, origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
])

api.add_resource(LoginUser, '/login')
api.add_resource(LogoutUser, '/logout')
api.add_resource(RegisterUser, '/register')

if __name__ == "__main__":
    app.run(debug=True)