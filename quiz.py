from flask import Flask, render_template, redirect, url_for, flash, session
from forms import AddQuestion, StartQuiz
from db import db, Quiz

app = Flask(__name__)

# set up database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my_secret_key'

# initialise db with SQLAlchemy init_app function
db.init_app(app)

@app.route("/", methods=["POST", "GET"])
def home():

    form = StartQuiz()

    if form.validate_on_submit():
        session["user"] = form.name.data

    return render_template("index.html", form=form)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for('home'))

@app.route('/start-quiz')
def start_quiz():
    return redirect(url_for('question'))

@app.route("/question")
def question():
    return render_template('question.html')

@app.route("/answer")
def answer():
    return render_template("answer.html")

@app.route("/add-question", methods=["POST", "GET"])
def add_question():

    form = AddQuestion()

    if form.validate_on_submit():
        new_question = Quiz(question=form.question.data, answer=form.answer.data)
        db.session.add(new_question)
        db.session.commit()
        flash('Question saved!', 'success')
        return redirect(url_for('add_question'))

    return render_template("add-question.html", form=form)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)