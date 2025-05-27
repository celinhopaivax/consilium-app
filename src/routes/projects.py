from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.models import db
from src.models.project import Project
from src.models.user import User # Import User if needed for project ownership or assignments
from src.models.task import Task # Import Task model
from sqlalchemy import desc # Import desc for ordering

projects_bp = Blueprint("projects_bp", __name__)

@projects_bp.route("/")
@login_required
def list_projects():
    # Query projects owned by or shared with the current user
    # For now, let's assume projects are owned by the user.
    projects = Project.query.filter_by(owner_id=current_user.id).order_by(Project.created_at.desc()).all()
    return render_template("projects/list.html", projects=projects)

@projects_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_project():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if not name:
            flash("O nome do projeto é obrigatório.", "danger")
            return render_template("projects/create_edit.html", title="Criar Novo Projeto")

        new_project = Project(name=name, description=description, owner_id=current_user.id)
        db.session.add(new_project)
        db.session.commit()

        # CORRIGIDO: Removido caracteres inválidos e quebra de linha
        flash(f'Projeto "{name}" criado com sucesso!', "success") 
        return redirect(url_for("projects_bp.list_projects"))
    
    return render_template("projects/create_edit.html", title="Criar Novo Projeto", project=None)

@projects_bp.route("/<int:project_id>")
@login_required
def view_project(project_id):
    project = Project.query.get_or_404(project_id)
    # Add authorization check: ensure current_user has access to this project
    if project.owner_id != current_user.id:
        flash("Você não tem permissão para ver este projeto.", "danger")
        return redirect(url_for("projects_bp.list_projects"))
    
    # CORRIGIDO: Buscar e ordenar tarefas aqui no Python
    tasks = Task.query.filter_by(project_id=project.id).order_by(desc(Task.created_at)).all()
    
    # Passar as tarefas ordenadas para o template
    return render_template("projects/view.html", project=project, tasks=tasks)

@projects_bp.route("/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.owner_id != current_user.id:
        flash("Você não tem permissão para editar este projeto.", "danger")
        return redirect(url_for("projects_bp.list_projects"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if not name:
            flash("O nome do projeto é obrigatório.", "danger")
            return render_template("projects/create_edit.html", title=f"Editar Projeto: {project.name}", project=project)

        project.name = name
        project.description = description
        db.session.commit()
        # CORRIGIDO: Removido caracteres inválidos e quebra de linha
        flash(f'Projeto "{project.name}" atualizado com sucesso!', "success") 
        return redirect(url_for("projects_bp.view_project", project_id=project.id))

    return render_template("projects/create_edit.html", title=f"Editar Projeto: {project.name}", project=project)

@projects_bp.route("/<int:project_id>/delete", methods=["POST"]) # Use POST for deletion
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.owner_id != current_user.id:
        flash("Você não tem permissão para excluir este projeto.", "danger")
        return redirect(url_for("projects_bp.list_projects"))

    # Add confirmation step in the template if desired
    db.session.delete(project)
    db.session.commit()
    # CORRIGIDO: Removido caracteres inválidos e quebra de linha
    flash(f'Projeto "{project.name}" excluído com sucesso.', "success") 
    return redirect(url_for("projects_bp.list_projects"))
