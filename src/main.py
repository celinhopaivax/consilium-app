import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import current_user

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

# Import init_login_manager from auth routes
from src.routes.auth import init_login_manager

app = Flask(__name__, 
            static_folder=os.path.join(os.path.dirname(__file__), 'static'),
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key_CHANGE_ME_IN_PRODUCTION')

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'consilium_db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask extensions
db.init_app(app)
migrate.init_app(app, db) # For database migrations
init_login_manager(app) # Initialize Flask-Login

# Import and register blueprints
from src.routes.auth import auth_bp
from src.routes.projects import projects_bp
from src.routes.tasks import tasks_bp
from src.routes.comments import comments_bp # Import comments blueprint

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(projects_bp, url_prefix='/projects')
app.register_blueprint(tasks_bp, url_prefix='/tasks')
app.register_blueprint(comments_bp, url_prefix='/comments') # Register comments blueprint

# Import models here to ensure they are registered with SQLAlchemy
from src.models import user, project, task, comment

# A simple main blueprint for general routes like index/dashboard
from flask import Blueprint
main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/')
def index():
    if current_user.is_authenticated:
        # Redirect to projects list as a more meaningful dashboard
        return redirect(url_for('projects_bp.list_projects'))
    return redirect(url_for('auth_bp.login'))

app.register_blueprint(main_routes) # Register without prefix for root URL

# Update base.html nav link for projects
@app.context_processor
def inject_nav_links():
    nav_links = []
    if current_user.is_authenticated:
        nav_links.append({'url': url_for('projects_bp.list_projects'), 'text': 'Meus Projetos'})
    return dict(nav_links=nav_links)

# Serve static files and index.html (fallback for SPA-like behavior or if specific assets are requested)
@app.route('/<path:path>')
def serve_static_path(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404
    
    if os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    return "Recurso não encontrado", 404


if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Creates database tables based on models
    app.run(host='0.0.0.0', port=5000, debug=True)

