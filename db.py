from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Quiz(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    question = db.Column(db.String(300))
    answer = db.Column(db.String(300))
    prev_response = db.Column(db.Boolean, default=False)