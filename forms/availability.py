from flask_wtf import FlaskForm
from wtforms.fields.datetime import TimeField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired


class AvailabilityForm(FlaskForm):
    start = TimeField('Start Time', format='%H:%M', validators=[DataRequired()])
    end = TimeField('End Time', format='%H:%M', validators=[DataRequired()])
    submit = SubmitField('Update Availability')
