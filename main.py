import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_pymongo import PyMongo

from UserLogin import UserLogin
from Meetings import *
from Month import Month
from UserAccount import UserAcc
from UserCreator import UserCreator


def run_demo():
    student1 = UserAcc("james", "james@gmail.com", 0, [])
    student2 = UserAcc("john", "john@gmail.com", 0, [])
    student3 = UserAcc("lucas", "lucas@gmail.com", 0, [])

    tutor1 = UserAcc("bond", "bond@ufl.edu", 1, [], ["algebra", "c++", "python"])

    tempString = "2025-07-04 8:01 pm"

    testMeet = Meeting(tutor1.email, tempString, 60, 6, tutor1.subject_list)
    testMeet.add_student(student1.email)
    testMeet.add_student(student2.email)
    testMeet.add_student(student3.email)
    testMeet.remove_student(student1.email)
    testMeet.print_details()

    testMonth = Month(7, 2025)
    testMonth.print_self()

    creator = UserCreator()
    print(creator.create_user(
        "Moises Sanchez",
        "Moises@testing.com",
        "Password123",
        "Student",
        ["Computer Science"]
    ))

    login = UserLogin()
    user_doc = login.login("Moises@testing.com", "Password123")
    if user_doc:
        print(user_doc["name"])
        print(user_doc["role"])
    else:
        print("Invalid Credentials")


# --- Flask App and frontend Integration ---
class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Account Type', choices=[('Student', 'Student'), ('Tutor', 'Tutor')], validators=[DataRequired()])
    subjects = StringField('Subjects (comma-separated)')
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
    doc = UserLogin.get_by_id(user_id)
    return User(doc) if doc else None


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        subjects = [s.strip() for s in form.subjects.data.split(',')] if form.subjects.data else []
        creator = UserCreator()
        success, message = creator.create_user(
            form.name.data,
            form.email.data,
            form.password.data,
            form.role.data,
            subjects
        )
        if success:
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
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
    run_demo()
    app.run(debug=True)
