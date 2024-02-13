from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField
from wtforms.validators import DataRequired, InputRequired, Length, Email, EqualTo, NumberRange

class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=3, max=15)])
    email = StringField('email',validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    confirm_password = PasswordField('confirm_password', validators=[DataRequired(), EqualTo('password')])
    submit_button = SubmitField('Register')


class LoginForm(FlaskForm):

    email = StringField('email',validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    submit_button = SubmitField('Login')


class AddLessonForm(FlaskForm):
    time_field = FloatField('time_field', validators=[InputRequired(), NumberRange(min=0, max=100)], default=0)
    content = StringField('content_field', validators=[DataRequired()])
    submit_button = SubmitField('Add lesson')
