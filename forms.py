from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class AddQuestion(FlaskForm):
    question = StringField('Question', validators=[DataRequired()])
    answer = StringField('Answer', validators=[DataRequired()])
    submit = SubmitField('Submit')

class StartQuiz(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class QuizForm(FlaskForm):
    question = StringField('Question', render_kw={'readonly': True})
    see_answer = SubmitField('Show answer')
    answer = StringField('Answer', render_kw={'readonly': True})
    incorrect = SubmitField('I got this wrong')
    correct = SubmitField('I got this right!')
