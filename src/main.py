# src/main.py
import datetime
import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, render_template, redirect, url_for
from flask_login import current_user

# Import extensions from the new extensions module
from src.extensions import db, migrate, login_manager, mail

def create_app():
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
        # Fallback to individual environment variables if DATABASE_URL is not set
        db_user_pg = os.getenv('DB_USERNAME_PG', 'postgres')
        db_pass_pg = os.getenv('DB_PASSWORD_PG', 'password')
        db_host_pg = os.getenv('DB_HOST_PG', 'localhost')
        db_port_pg = os.getenv('DB_PORT_PG', '5432')
        db_name_pg = os.getenv('DB_NAME_PG', 'consilium_db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_user_pg}:{db_pass_pg}@{db_host_pg}:{db_port_pg}/{db_name_pg}"

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Flask-Mail configuration (using environment variables)
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your-email@example.com')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your-email-password')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

    # Initialize Flask extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    # Import models here AFTER db is initialized and within app context if needed
    # It's better to import models where they are needed (routes, etc.)
    # but we need User for the user_loader
    from src.models.user import User

    # Define user_loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import and register blueprints
    from src.routes.auth import auth_bp
    from src.routes.projects import projects_bp
    from src.routes.tasks import tasks_bp
    from src.routes.comments import comments_bp
    # Import main routes blueprint if you have one
    # from src.routes.main import main_bp 

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(comments_bp, url_prefix='/comments')
    # app.register_blueprint(main_bp)

    # --- Define main index route directly here or in a separate main routes file ---
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('projects_bp.list_projects'))
        return redirect(url_for('auth_bp.login'))
    # -----------------------------------------------------------------------------

    # Context processors
    @app.context_processor
    def inject_nav_links():
        nav_links = []
        if current_user.is_authenticated:
            # Corrected endpoint name
            nav_links.append({'url': url_for('projects_bp.list_projects'), 'text': 'Projetos'})
        return dict(nav_links=nav_links)

    @app.context_processor
    def inject_current_year():
        return {"current_year": datetime.datetime.now().year}

    # Serve static files fallback (Optional, usually handled by Flask automatically)
    # @app.route('/<path:path>')
    # def serve_static_path(path):
    #     static_folder_path = app.static_folder
    #     if static_folder_path is None:
    #         return "Static folder not configured", 404
    #     
    #     if os.path.exists(os.path.join(static_folder_path, path)):
    #         return send_from_directory(static_folder_path, path)
    #     return "Recurso não encontrado", 404

    return app

# Create the Flask app instance using the factory function
app = create_app()

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.getenv('PORT', 5000))
    # Run the app (debug=False for production)
    # Use waitress or gunicorn in production instead of app.run()
    # For Fly.io, the Procfile or fly.toml handles the server (gunicorn or python directly)
    # This block might not be strictly necessary if using a Procfile/gunicorn
    # but it allows running locally with `python src/main.py` if needed.
    # Ensure debug=False is set here if running this way in production (though not recommended).
    app.run(host='0.0.0.0', port=port, debug=False)

