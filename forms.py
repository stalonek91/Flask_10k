from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Length, Email, EqualTo

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=3, max=15)])
    email = StringField('email',validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    confirm_password = PasswordField('confirm_password', validators=[DataRequired(), EqualTo('password')])
    submit_button = SubmitField('submit')