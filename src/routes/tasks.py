from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user
# Import db and mail from extensions
from src.extensions import db, mail 
from src.models.task import Task
from src.models.project import Project
from src.models.user import User # For assigning tasks
import datetime
from flask_mail import Message # Import Message for email
import threading # To send email in background

tasks_bp = Blueprint("tasks_bp", __name__)

# Helper function to send email asynchronously
def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            # Use Flask's built-in logger
            app.logger.error(f"Erro ao enviar e-mail: {e}") 

def send_task_assignment_email(app, task, assignee):
    if not assignee or not assignee.email:
        app.logger.warning(f"Tentativa de enviar e-mail para tarefa {task.id} sem e-mail de destinatário.")
        return # Cannot send email without recipient address
    
    project = Project.query.get(task.project_id)
    subject = f"Nova tarefa atribuída a você: {task.title}"
    sender = app.config.get("MAIL_DEFAULT_SENDER")
    if not sender:
        app.logger.error("MAIL_DEFAULT_SENDER não configurado.")
        return
        
    recipients = [assignee.email]
    # Create a simple HTML body (consider using templates for more complex emails)
    # Ensure _external=True for url_for to generate absolute URLs needed in emails
    project_url = url_for("projects_bp.view_project", project_id=task.project_id, _external=True)
    html_body = f"""
    <p>Olá {assignee.username},</p>
    <p>Uma nova tarefa foi atribuída a você no projeto <strong>{project.name if project else "desconhecido"}</strong>:</p>
    <p><strong>Tarefa:</strong> {task.title}</p>
    <p><strong>Descrição:</strong> {task.description if task.description else "N/A"}</p>
    <p><strong>Prazo:</strong> {task.due_date.strftime("%d/%m/%Y") if task.due_date else "Não definido"}</p>
    <p>Você pode ver os detalhes do projeto <a href="{project_url}">aqui</a>.</p>
    <p>Atenciosamente,<br>Sistema Consilium</p>
    """
    msg = Message(subject, sender=sender, recipients=recipients, html=html_body)
    
    # Send email in a separate thread to avoid blocking the request
    thread = threading.Thread(target=send_async_email, args=[app, msg])
    thread.start()

# Helper function to check project access (simplified as per previous changes)
def check_project_access(project_id):
    project = Project.query.get_or_404(project_id)
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
                    # Return here to prevent creating task with invalid date
                    users = User.query.order_by(User.username).all()
                    return render_template("tasks/create_edit.html", title="Criar Nova Tarefa", project=project, task=None, users=users)
            
            assignee_id = None
            assignee = None
            if assignee_id_str and assignee_id_str.isdigit():
                assignee_id = int(assignee_id_str)
                assignee = User.query.get(assignee_id)
                if not assignee:
                    flash("Usuário atribuído inválido.", "warning")
                    assignee_id = None # Reset assignee_id if user not found

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
            flash(f"Tarefa \"{title}\" criada com sucesso!", "success") # Corrected f-string syntax
            
            # Send email notification if assignee was set
            if assignee:
                # Pass the current app context correctly
                send_task_assignment_email(current_app._get_current_object(), new_task, assignee)
                
            return redirect(url_for("projects_bp.view_project", project_id=project.id))
    
    # Fetch users ordered by username for the dropdown
    users = User.query.order_by(User.username).all()
    return render_template("tasks/create_edit.html", title="Criar Nova Tarefa", project=project, task=None, users=users)

@tasks_bp.route("/task/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = check_project_access(task.project_id)
    old_assignee_id = task.assignee_id # Store old assignee to check if it changed

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
                    # Return here to prevent saving with invalid date
                    users = User.query.order_by(User.username).all()
                    return render_template("tasks/create_edit.html", title=f"Editar Tarefa: {task.title}", project=project, task=task, users=users)
            else:
                task.due_date = None
            
            new_assignee_id = None
            new_assignee = None
            if assignee_id_str and assignee_id_str.isdigit():
                new_assignee_id = int(assignee_id_str)
                new_assignee = User.query.get(new_assignee_id)
                if new_assignee:
                    task.assignee_id = new_assignee_id
                else:
                    flash("Usuário atribuído inválido.", "warning")
                    task.assignee_id = None # Unassign if invalid user selected
            else:
                task.assignee_id = None # Unassign if selection is empty or not a digit

            # Check if status changed to Concluído to set completed_at
            if task.status == "Concluído" and not task.completed_at:
                 task.completed_at = datetime.datetime.utcnow()
            elif task.status != "Concluído":
                 task.completed_at = None # Reset if status changes from Concluído

            db.session.commit()
            flash(f"Tarefa \"{task.title}\" atualizada com sucesso!", "success") # Corrected f-string syntax
            
            # Send email notification if assignee changed to a new user
            if new_assignee and task.assignee_id == new_assignee.id and task.assignee_id != old_assignee_id:
                send_task_assignment_email(current_app._get_current_object(), task, new_assignee)
                
            return redirect(url_for("projects_bp.view_project", project_id=project.id))

    # Fetch users ordered by username for the dropdown
    users = User.query.order_by(User.username).all()
    return render_template("tasks/create_edit.html", title=f"Editar Tarefa: {task.title}", project=project, task=task, users=users)

@tasks_bp.route("/task/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = check_project_access(task.project_id)
    
    # Restrict deletion to project owner
    if project.owner_id != current_user.id:
         flash("Você não tem permissão para excluir tarefas neste projeto.", "danger")
         # Use abort(403) for permission denied
         abort(403) 

    db.session.delete(task)
    db.session.commit()
    flash(f"Tarefa \"{task.title}\" excluída com sucesso.", "success") # Corrected f-string syntax
    return redirect(url_for("projects_bp.view_project", project_id=project.id))

@tasks_bp.route("/task/<int:task_id>/update_status", methods=["POST"])
@login_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    project = check_project_access(task.project_id)
    
    new_status = request.form.get("status")
    if new_status and new_status in ["A Fazer", "Em Andamento", "Concluído"]: # Validate status
        task.status = new_status
        # Set completed_at when status changes to Concluído
        if new_status == "Concluído" and not task.completed_at:
            task.completed_at = datetime.datetime.utcnow()
        elif new_status != "Concluído":
            task.completed_at = None # Reset if status changes from Concluído
            
        db.session.commit()
        flash(f"Status da tarefa \"{task.title}\" atualizado para \"{new_status}\".", "success") # Corrected f-string syntax
    else:
        flash("Status inválido.", "danger")
    return redirect(url_for("projects_bp.view_project", project_id=project.id))

