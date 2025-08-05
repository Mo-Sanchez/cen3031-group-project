# ---------- form ----------
from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

#Flask WTF form used for authenticating users by collecting email and password input
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')