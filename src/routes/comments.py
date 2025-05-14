from flask import Blueprint, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from src.models import db
from src.models.comment import Comment
from src.models.task import Task
from src.models.project import Project # To verify project access through task

comments_bp = Blueprint("comments_bp", __name__)

# Helper function to check project ownership or membership (if implemented)
# This ensures that the user commenting has access to the project the task belongs to.
def check_task_project_access(task_id):
    task = Task.query.get_or_404(task_id)
    project = Project.query.get_or_404(task.project_id)
    if project.owner_id != current_user.id:
        # In a more complex app, you might check for project membership too
        abort(403) # Forbidden
    return task, project

@comments_bp.route("/task/<int:task_id>/comment/add", methods=["POST"])
@login_required
def add_comment(task_id):
    task, project = check_task_project_access(task_id)
    
    content = request.form.get("comment_content")

    if not content or not content.strip():
        flash("O conteúdo do comentário não pode estar vazio.", "danger")
    else:
        new_comment = Comment(content=content, task_id=task.id, author_id=current_user.id)
        db.session.add(new_comment)
        db.session.commit()
        flash("Comentário adicionado com sucesso!", "success")
    
    # Redirect back to the project view, which should ideally show tasks and their details including comments.
    # Or, if you have a dedicated task view page:
    # return redirect(url_for("tasks_bp.view_task", task_id=task.id))
    return redirect(url_for("projects_bp.view_project", project_id=project.id))

# Deleting comments could be added here if required by RF014 (implicitly, if comments are displayed, they might need management)
# @comments_bp.route("/comment/<int:comment_id>/delete", methods=["POST"])
# @login_required
# def delete_comment(comment_id):
#     comment = Comment.query.get_or_404(comment_id)
#     task, project = check_task_project_access(comment.task_id)
#     if comment.author_id != current_user.id and project.owner_id != current_user.id: # Allow author or project owner to delete
#         flash("Você não tem permissão para excluir este comentário.", "danger")
#         abort(403)
    
#     db.session.delete(comment)
#     db.session.commit()
#     flash("Comentário excluído com sucesso.", "success")
#     return redirect(url_for("projects_bp.view_project", project_id=project.id))

