from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from src.models import db
from src.models.user import User

auth_bp = Blueprint("auth_bp", __name__)

login_manager = LoginManager()

# This function needs to be called in your main app factory (e.g., in src/main.py or src/__init__.py)
def init_login_manager(app):
    login_manager.init_app(app)
    login_manager.login_view = "auth_bp.login"  # The route for login page
    login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main_routes.index")) # Assuming a main blueprint for dashboard
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            flash("Todos os campos são obrigatórios.", "danger")
            return render_template("auth/register.html")

        if User.query.filter_by(email=email).first():
            flash("Este e-mail já está cadastrado.", "warning")
            return render_template("auth/register.html", username=username, email=email)
        
        if User.query.filter_by(username=username).first():
            flash("Este nome de usuário já está em uso.", "warning")
            return render_template("auth/register.html", username=username, email=email)

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Cadastro realizado com sucesso! Faça o login.", "success")
        return redirect(url_for("auth_bp.login"))
    return render_template("auth/register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main_routes.index")) # Assuming a main blueprint for dashboard

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = True if request.form.get("remember") else False

        if not email or not password:
            flash("E-mail e senha são obrigatórios.", "danger")
            return render_template("auth/login.html")

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("E-mail ou senha inválidos.", "danger")
            return render_template("auth/login.html", email=email)
        
        login_user(user, remember=remember)
        flash("Login realizado com sucesso!", "success")
        # Redirect to a protected page, e.g., dashboard or projects list
        # For now, let's assume a route named 'projects_bp.list_projects'
        # This will need to be created later.
        # return redirect(url_for('projects_bp.list_projects')) 
        return redirect(url_for("main_routes.index")) # Placeholder, change to actual dashboard/projects page

    return render_template("auth/login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você foi desconectado.", "info")
    return redirect(url_for("auth_bp.login"))

