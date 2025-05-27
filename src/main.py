import datetime
import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, render_template, redirect, url_for
from flask_migrate import Migrate
from flask_login import current_user
from flask_mail import Mail # Import Flask-Mail

# Importa a instância db de src.models
from src.models import db 

# Initialize extensions (db já foi importado)
migrate = Migrate()
mail = Mail() # Initialize Mail

# Import init_login_manager from auth routes
from src.routes.auth import init_login_manager

app = Flask(__name__, 
            static_folder=os.path.join(os.path.dirname(__file__), 'static'),
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key_CHANGE_ME_IN_PRODUCTION')

# Database Configuration - PostgreSQL
database_url = os.getenv('DATABASE_URL')
if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    db_user_pg = os.getenv('DB_USERNAME_PG', os.getenv('DB_USERNAME', 'postgres'))
    db_pass_pg = os.getenv('DB_PASSWORD_PG', os.getenv('DB_PASSWORD', 'password'))
    db_host_pg = os.getenv('DB_HOST_PG', os.getenv('DB_HOST', 'localhost'))
    db_port_pg = os.getenv('DB_PORT_PG', os.getenv('DB_PORT', '5432'))
    db_name_pg = os.getenv('DB_NAME_PG', os.getenv('DB_NAME', 'consilium_db'))
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_user_pg}:{db_pass_pg}@{db_host_pg}:{db_port_pg}/{db_name_pg}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail configuration (using environment variables)
# IMPORTANT: User needs to set these environment variables in Fly.io secrets
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.example.com') # e.g., smtp.gmail.com
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your-email@example.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your-email-password')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

# Initialize Flask extensions
db.init_app(app)
migrate.init_app(app, db)
init_login_manager(app)
mail.init_app(app) # Initialize Flask-Mail with app

# Import and register blueprints
from src.routes.auth import auth_bp
from src.routes.projects import projects_bp
from src.routes.tasks import tasks_bp
from src.routes.comments import comments_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(projects_bp, url_prefix='/projects')
app.register_blueprint(tasks_bp, url_prefix='/tasks')
app.register_blueprint(comments_bp, url_prefix='/comments')

# Import models here
from src.models import user, project, task, comment

# Main blueprint
from flask import Blueprint
main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('projects_bp.list_projects'))
    return redirect(url_for('auth_bp.login'))

app.register_blueprint(main_routes)

# Context processors
@app.context_processor
def inject_nav_links():
    nav_links = []
    if current_user.is_authenticated:
        nav_links.append({'url': url_for('projects_bp.list_projects'), 'text': 'Meus Projetos'})
    return dict(nav_links=nav_links)

@app.context_processor
def inject_current_year():
    return {"current_year": datetime.datetime.now().year}

# Serve static files fallback
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
        # db.create_all() # REMOVIDO - Usar migrações ou garantir que foi executado uma vez
        pass 
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
