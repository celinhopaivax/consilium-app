from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from src.models import db
from src.models.task import Task
from src.models.project import Project
from src.models.user import User # For assigning tasks
import datetime

tasks_bp = Blueprint("tasks_bp", __name__)

# Helper function to check project ownership or membership (if implemented)
def check_project_access(project_id):
    project = Project.query.get_or_404(project_id)
    if project.owner_id != current_user.id:
        # In a more complex app, you might check for project membership too
        abort(403) # Forbidden
    return project

@tasks_bp.route("/project/<int:project_id>/tasks/create", methods=["GET", "POST"])
@login_required
def create_task(project_id):
    project = check_project_access(project_id)

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        status = request.form.get("status", "A Fazer")
        due_date_str = request.form.get("due_date")
        assignee_id_str = request.form.get("assignee_id")

        if not title:
            flash("O título da tarefa é obrigatório.", "danger")
        else:
            due_date = None
            if due_date_str:
                try:
                    due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
                except ValueError:
                    flash("Formato de data inválido. Use YYYY-MM-DD.", "danger")
                    # Consider re-rendering form with errors
            
            assignee_id = None
            if assignee_id_str and assignee_id_str.isdigit():
                assignee_id = int(assignee_id_str)
                # Optional: Check if assignee is part of the project or a valid user
                if not User.query.get(assignee_id):
                    flash("Usuário atribuído inválido.", "warning")
                    assignee_id = None # Reset if invalid

            new_task = Task(
                title=title, 
                description=description, 
                status=status, 
                due_date=due_date, 
                project_id=project.id,
                assignee_id=assignee_id
            )
            db.session.add(new_task)
            db.session.commit()
                 flash(f"Tarefa {"{title}"} criada com sucesso!")
            return redirect(url_for("projects_bp.view_project", project_id=project.id))
    
    # For GET request or if POST fails validation and needs re-render
    # Pass users for assignee dropdown (simplified: all users for now)
    users = User.query.all()
    return render_template("tasks/create_edit.html", title="Criar Nova Tarefa", project=project, task=None, users=users)

@tasks_bp.route("/task/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = check_project_access(task.project_id) # Ensures user has access to the project of the task

    if request.method == "POST":
        task.title = request.form.get("title")
        task.description = request.form.get("description")
        task.status = request.form.get("status")
        due_date_str = request.form.get("due_date")
        assignee_id_str = request.form.get("assignee_id")

        if not task.title:
            flash("O título da tarefa é obrigatório.", "danger")
        else:
            if due_date_str:
                try:
                    task.due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
                except ValueError:
                    flash("Formato de data inválido. Use YYYY-MM-DD.", "danger")
            else:
                task.due_date = None
            
            assignee_id = None
            if assignee_id_str and assignee_id_str.isdigit():
                assignee_id = int(assignee_id_str)
                if User.query.get(assignee_id):
                    task.assignee_id = assignee_id
                else:
                    flash("Usuário atribuído inválido.", "warning")
                    task.assignee_id = None # Or keep old one, depending on desired logic
            else:
                task.assignee_id = None # Unassign if empty or invalid

            db.session.commit()
            flash(f"Tarefa 
ások{"{task.title}"} atualizada com sucesso!", "success")
            return redirect(url_for("projects_bp.view_project", project_id=project.id))

    users = User.query.all()
    return render_template("tasks/create_edit.html", title=f"Editar Tarefa: {task.title}", project=project, task=task, users=users)

@tasks_bp.route("/task/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = check_project_access(task.project_id)

    db.session.delete(task)
    db.session.commit()
    flash(f"Tarefa 
ások{"{task.title}"} excluída com sucesso.", "success")
    return redirect(url_for("projects_bp.view_project", project_id=project.id))

@tasks_bp.route("/task/<int:task_id>/update_status", methods=["POST"])
@login_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    project = check_project_access(task.project_id)
    
    new_status = request.form.get("status")
    if new_status and new_status in ["A Fazer", "Em Andamento", "Concluído"]: # Validate status
        task.status = new_status
        db.session.commit()
        flash(f"Status da tarefa 
ások{"{task.title}"} atualizado para 
ások{"{new_status}"}.", "success")
    else:
        flash("Status inválido.", "danger")
    return redirect(url_for("projects_bp.view_project", project_id=project.id))

# Future: Route for viewing a single task with its comments
# @tasks_bp.route("/task/<int:task_id>")
# @login_required
# def view_task(task_id):
#     task = Task.query.get_or_404(task_id)
#     project = check_project_access(task.project_id)
#     # Fetch comments for this task
#     return render_template("tasks/view.html", task=task, project=project)

