from flask import Flask, render_template, redirect, url_for, flash, session, request
from forms import AddQuestion, StartQuiz, QuizForm, DeleteQuestions
from db import db, Quiz

app = Flask(__name__)

# set up database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my_secret_key'

# initialise db with SQLAlchemy init_app function
db.init_app(app)

def get_questions_data():
    # get all question data from database
    questions = Quiz.query.all()
    # transform Quiz objects into json serialisable form (dictionary), otherwise there is an error when setting to the session
    questions_data = [{'id': q._id, 'question': q.question, 'answer': q.answer} for q in questions]
    return questions_data

def initialise_quiz_session():
    """
    Initialize the quiz session by retrieving questions from the database and storing them in the session.
    """
    questions_data = get_questions_data()

    # store questions in the session
    session['questions'] = questions_data
    session['current_q_index'] = 0
    session['current_a_index'] = 0
    session['number_of_questions'] = len(questions_data)
    session['user_responses'] = []
    session['show_answer'] = False

@app.route("/", methods=["POST", "GET"])
def home():
    """
    Route for the home page. Handles user login and renders the home page template.
    """

    form = StartQuiz()

    if form.validate_on_submit():
        # set user session variable
        session["user"] = form.name.data

    return render_template("index.html", form=form)

@app.route("/logout")
def logout():
    """
    Route for logging out. Removes the user from the session and redirects to the home page.
    """

    session.pop("user", None)
    return redirect(url_for('home'))

@app.route('/start-quiz')
def start_quiz():
    """
    Route to start the quiz. Redirects to the quiz route after initializing the quiz session.
    """

    if 'user' not in session:
        return redirect(url_for('home'))
    
    initialise_quiz_session()

    return redirect(url_for('quiz'))

@app.route("/quiz", methods=["POST", "GET"])
def quiz():
    """
    Route for handling the quiz. Manages quiz logic, question display, and user responses.
    """

    if 'user' not in session or 'questions' not in session:
        return redirect(url_for('home'))
    
    number_of_questions = session.get('number_of_questions')
    if number_of_questions < 1:
        flash('Number of questions cannot be zero', 'error')
        return redirect(url_for('home'))

    current_question_index = session.get('current_q_index')
    current_answer_index = session.get('current_a_index')
    questions = session['questions']
    show_answer = session.get('show_answer', False)

    form = QuizForm()

    # show first question
    if current_question_index == 0 and not show_answer:
        question = questions[current_question_index]['question']
        session['show_answer'] = True
        session['current_q_index'] += 1 
        displayed_q_num = current_question_index + 1
        return render_template('quiz.html',
                               form=form, 
                               question=question,
                               current_question_index=current_question_index,
                               number_of_questions=number_of_questions,
                               displayed_q_num=displayed_q_num
                               )

    if form.validate_on_submit():
        # check if last question has been asked
        if current_question_index == number_of_questions and current_answer_index == number_of_questions:
            end_of_quiz = True
        else:
            end_of_quiz = False

        # record answer if provided (current_question_index has been incremented so it's -1)
        if form.incorrect.data:
            # handle incorrect answer report
            session['user_responses'] = record_results(current_question_index - 1, False, questions[current_question_index - 1]['id'])
        elif form.correct.data:
            # handle correct answer report
            session['user_responses'] = record_results(current_question_index - 1, True, questions[current_question_index - 1]['id'])
        
        if end_of_quiz:
            print("ending quiz")
            return redirect(url_for('results'))

        # show question or answer
        if not show_answer:
            question = questions[current_question_index]['question']
            session['show_answer'] = True
            session['current_q_index'] += 1 
            displayed_q_num = current_question_index + 1
            return render_template('quiz.html', 
                                   form=form, 
                                   question=question, 
                                   current_question_index=current_question_index, 
                                   number_of_questions=number_of_questions,
                                   displayed_q_num=displayed_q_num
                                   )
        else:
            answer = questions[current_answer_index]['answer']
            session['show_answer'] = False
            session['current_a_index'] += 1
            displayed_q_num = current_answer_index + 1
            return render_template('quiz.html',
                                   form=form,
                                   answer=answer,
                                   current_answer_index=current_answer_index,
                                   number_of_questions=number_of_questions,
                                   displayed_q_num=displayed_q_num
                                   )

def record_results(current_question_index, q_response, id):
    """
    Returns a dictionary of all user reponses
    """
    responses = session['user_responses']
    responses.append({'id': id, 'index': current_question_index, 'answer_correct': q_response})
    return responses

@app.route("/results")
def results():
    """
    Route for displaying the quiz results.
    """
    user_responses = session['user_responses']
    return render_template("results.html", user_responses=user_responses)

@app.route("/list-questions", methods=["POST", "GET"])
def list_questions():
    questions = Quiz.query.all()
    delete_forms = [DeleteQuestions(prefix=str(question._id)) for question in questions]

    if request.method == 'POST':
        # check for submitted delete forms
        for question, delete_form in zip(questions, delete_forms):
            if delete_form.delete.data and delete_form.validate:
                db.session.delete(question)
                db.session.commit()
                flash('Question deleted', 'success')
                return redirect(url_for('list_questions'))

    return render_template("list-questions.html", delete_forms=delete_forms, questions=questions)

@app.route("/add-question", methods=["POST", "GET"])
def add_question():
    """
    Route for adding a new quiz question. Handles form submission and database update.
    """
    form = AddQuestion()

    if form.validate_on_submit():
        new_question = Quiz(question=form.question.data, answer=form.answer.data)
        db.session.add(new_question)
        db.session.commit()
        flash('Question saved!', 'success')
        return redirect(url_for('add_question'))

    return render_template("add-question.html", form=form)

@app.route("/edit-question", methods=["POST", "GET"])
def edit_question():
    # edit question
    return

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)