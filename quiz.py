from flask import Flask, render_template, request
from db import db, Quiz

app = Flask(__name__)

# set up database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# initialise db with SQLAlchemy init_app function
db.init_app(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/question")
def question():
    return render_template("question.html")

@app.route("/answer")
def answer():
    return render_template("answer.html")

@app.route("/create", methods=["POST", "GET"])
def create():
    if request.method == "POST":
    
        return render_template("create.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)