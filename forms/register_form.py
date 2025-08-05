from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

#Returns a list of time strings at 30 minute intervals across a day used for availability selection
def half_hour_choices():
    return [(f"{h:02d}:{m:02d}", f"{h:02d}:{m:02d}")
            for h in range(24) for m in (0, 30)]

#Flask WTF form for creating a new user account for either students or tutors
class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Account Type',
                       choices=[('Student', 'Student'), ('Tutor', 'Tutor')],
                       validators=[DataRequired()])
    subject = StringField('Subject', validators=[Optional()])
    start_avail = SelectField('Start Availability',
                              choices=half_hour_choices(), validators=[Optional()])
    end_avail = SelectField('End Availability',
                            choices=half_hour_choices(), validators=[Optional()])
    submit = SubmitField('Register')