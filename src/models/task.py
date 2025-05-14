from . import db # Import db from the current package (src.models)
import datetime

class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default="A Fazer") # e.g., "A Fazer", "Em Andamento", "Concluído"
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    project = db.relationship("Project", back_populates="tasks")
    assignee = db.relationship("User", back_populates="tasks_assigned", foreign_keys=[assignee_id])
    comments = db.relationship("Comment", back_populates="task", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Task {self.title}>"

