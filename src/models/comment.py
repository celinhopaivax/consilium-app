from . import db # Import db from the current package (src.models)
import datetime

class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    task = db.relationship("Task", back_populates="comments")
    author = db.relationship("User", back_populates="comments", foreign_keys=[author_id])

    def __repr__(self):
        return f"<Comment {self.id} on Task {self.task_id}>"

