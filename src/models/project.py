from . import db # Import db from the current package (src.models)
import datetime

class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    owner = db.relationship("User", back_populates="projects_owned", foreign_keys=[owner_id])
    tasks = db.relationship("Task", back_populates="project", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.name}>"

