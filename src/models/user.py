from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db # Import db from the current package (src.models)
import datetime

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    projects_owned = db.relationship("Project", back_populates="owner", lazy="dynamic", foreign_keys="Project.owner_id")
    tasks_assigned = db.relationship("Task", back_populates="assignee", lazy="dynamic", foreign_keys="Task.assignee_id")
    comments = db.relationship("Comment", back_populates="author", lazy="dynamic", foreign_keys="Comment.author_id")

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

