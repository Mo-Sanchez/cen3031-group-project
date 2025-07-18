import os

from bson import ObjectId
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_pymongo import PyMongo

from UserLogin import UserLogin
from Meetings import MeetingObj
from Month import Month
from UserInstance import UserInstance
from UserCreator import UserCreator

from Demos import *


# --- Flask App and frontend Integration ---
class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Account Type', choices=[('Student', 'Student'), ('Tutor', 'Tutor')],
                       validators=[DataRequired()])

    # {% if form.role.data == 'Tutor' %}
    subjects = StringField('Subjects (comma-separated)')
    sun_start = StringField('Sunday start')
    sun_end = StringField('Sunday end')
    mon_start = StringField('Monday start')
    mon_end = StringField('Monday end')
    tue_start = StringField('Tuesday start')
    tue_end = StringField('Tuesday end')
    wed_start = StringField('Wednesday start')
    wed_end = StringField('Wednesday end')
    thu_start = StringField('Thursday start')
    thu_end = StringField('Thursday end')
    fri_start = StringField('Friday start')
    fri_end = StringField('Friday end')
    sat_start = StringField('Saturday start')
    sat_end = StringField('Saturday end')
    # {% endif %}

    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/tutorsched')

mongo = PyMongo(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, user_doc):
        self.id = str(user_doc['_id'])
        self.name = user_doc['name']
        self.email = user_doc['email']
        self.role = user_doc['role']


@login_manager.user_loader
def load_user(user_id):
    doc = UserLogin().users.find_one({"_id": ObjectId(user_id)})
    return User(doc) if doc else None


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    success = False
    message = ""
    if form.validate_on_submit():
        subjects = [s.strip() for s in form.subjects.data.split(',')] if form.subjects.data else []

        creator = UserCreator()
        if form.role.data == "Tutor":
            raw_input = {
                'sunday': [form.sun_start.data, form.sun_end.data],
                'monday': [form.mon_start.data, form.mon_end.data],
                'tuesday': [form.tue_start.data, form.tue_end.data],
                'wednesday': [form.wed_start.data, form.wed_end.data],
                'thursday': [form.thu_start.data, form.thu_end.data],
                'friday': [form.fri_start.data, form.fri_end.data],
                'saturday': [form.sat_start.data, form.sat_end.data]
            }

            availability = {}
            for day, (start, end) in raw_input.items():
                if start and end and end > start:
                    availability[day] = (start, end)
                else:
                    availability[day] = None

            success, message = creator.create_tutor_user(
                form.name.data,
                form.email.data,
                form.password.data,
                form.role.data,
                subjects,
                0,
                availability
            )
        else:
            success, message = creator.create_student_user(
                form.name.data,
                form.email.data,
                form.password.data,
                form.role.data,
            )

    if success:
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    elif message:
        flash(message, 'danger')


    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        authenticator = UserLogin()
        user_doc = authenticator.login(form.email.data, form.password.data)
        if user_doc:
            user = User(user_doc)
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    meetings = []
    return render_template('dashboard.html', meetings=meetings)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    runApp = input("Run the app? (Y/N)\n")
    if runApp == "Y":
        app.run(debug=True)
    else:
        while True:  # Looping until a viable demo is chosen
            choice = input("Choose your demo: \n1. 1_1\n2. 1_2 \n3. 2_1\n")
            if choice == "1":
                run_demo1_1()
                break
            elif choice == "2":
                run_demo1_2()
                break
            elif choice == "3":
                run_demo2_1()
            else:
                print("invalid input")

        while True:  # Looping for login testings
            print("Enter \"quit\" to cancel")
            email = input("Enter email: ")
            if email == "quit":
                break
            password = input("Enter password: ")
            if password == "quit":
                break
            login = UserLogin()
            user_doc = login.login(email, password)
            if user_doc:  # If the user is logged in
                ourUser = UserInstance(user_doc["_id"])
                ourUser.print_details()
            else:
                print("Invalid Credentials")  # if the user is not logged in, then print "Invalid Credentials"
