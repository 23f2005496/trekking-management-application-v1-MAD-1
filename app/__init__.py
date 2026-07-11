from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv

migrate = Migrate()

login_manager = LoginManager()

db = SQLAlchemy()

def create_app():
    
    load_dotenv()
    
    app = Flask(__name__)
    app.config.from_object('config.settings.Config')
    
    db.init_app(app)
    migrate.init_app(app, db) 
    login_manager.init_app(app)

    return app

