from flask import Flask
from flask_login import LoginManager
from datetime import timedelta
from models import database, Users
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import json
from users import user
from views import views

with open("config.json", 'r') as file:
    data = json.load(file)
DB_NAME = data.get('DB_NAME')
SECRET_KEY = data.get('KEY')

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}.db"
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_REFRESH_EACH_REQUEST'] = False
    UPLOAD = 'static'
    app.config['UPLOAD_FOLDER'] = UPLOAD
    app.app_context().push()
    app.register_blueprint(user)
    app.register_blueprint(views)

    login_manager = LoginManager()
    login_manager.login_view = "user.signin"
    login_manager.init_app(app)
    app.permanent_session_lifetime = timedelta(minutes=60)

    @login_manager.user_loader
    def load_user(id):
            engine = create_engine(f'sqlite:///{DB_NAME}.db')
            database.metadata.create_all(engine)
            Session = sessionmaker(bind=engine)
            session = Session()
            user= session.query(Users).get(int(id))
            return user

    return app