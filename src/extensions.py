# src/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

# Configure login manager
login_manager.login_view = "auth_bp.login"
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "info"

# User loader function needs to be defined here or imported and set
# We will set it in main.py after importing User model to avoid circular imports
# @login_manager.user_loader
# def load_user(user_id):
#     # Import User model here locally if needed, or better, set this in main.py
#     from src.models.user import User 
#     return User.query.get(int(user_id))

