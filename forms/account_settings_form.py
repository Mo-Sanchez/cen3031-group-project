from flask_wtf import FlaskForm
from wtforms.fields.simple import SubmitField, HiddenField, StringField
from wtforms.validators import DataRequired

# Flask-WTF form used for updating a user's name or account deletion
class AccountSettingsForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Save')
    delete = HiddenField(
        'data',
        render_kw={'id': 'data'},
        default="None"
    )