from flask import Flask, render_template, redirect, url_for, flash, session
from forms import AddQuestion, StartQuiz, Question, Answer
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
    if 'user' not in session:
        return redirect(url_for('home'))
    
    questions = Quiz.query.all() # get all question data from database

    # transform Quiz objects into json serialisable form (dictionaries), otherwise there is an error when setting to the session
    questions_data = [{'id': q._id, 'question': q.question, 'answer': q.answer} for q in questions]

    # store questions in the session
    session['questions'] = questions_data
    session['current_index'] = 0
    session['number_of_questions'] = len(questions_data)
    session['user_responses'] = []
    session['show_answer'] = False

    return redirect(url_for('quiz'))

@app.route("/quiz", methods=["POST", "GET"])
def quiz():

    if 'user' not in session or 'questions' not in session:
        return redirect(url_for('home'))
    
    number_of_questions = session.get('number_of_questions')
    if number_of_questions < 1:
        flash('Number of questions cannot be zero', 'error')
        return redirect(url_for('home'))

    current_question_index = session.get('current_index')
    questions = session['questions']
    show_answer = session.get('show_answer', False)

    form = Question() if not show_answer else Answer()

    # show first question
    if current_question_index == 0 and not show_answer:
        question = questions[current_question_index]['question']
        session['show_answer'] = True
        return render_template('quiz.html',
                               form=form, 
                               question=question,
                               current_question_index=current_question_index,
                               number_of_questions=number_of_questions
                               )

    if form.validate_on_submit():
        if current_question_index == number_of_questions:
            return redirect(url_for('results'))
        if not show_answer:
            # add answer to user_responses
            question = questions[current_question_index]['question']
            session['show_answer'] = True
            return render_template('quiz.html', 
                                   form=form, 
                                   question=question, 
                                   current_question_index=current_question_index, 
                                   number_of_questions=number_of_questions
                                   )
        else:
            session['current_index'] += 1
            answer = questions[current_question_index]['answer']
            session['show_answer'] = False
            return render_template('quiz.html',
                                   form=form,
                                   answer=answer,
                                   current_question_index=current_question_index,
                                   number_of_questions=number_of_questions
                                   )


@app.route("/results")
def results():
    return render_template("results.html")

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