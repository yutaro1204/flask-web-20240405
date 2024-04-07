from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email

class SignUpForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(), Length(min=1, max=20)])
    email = StringField('email', validators=[InputRequired(), Email()])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=20)])

class SignInForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email()])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=20)])

class SignOutForm(FlaskForm):
    pass
