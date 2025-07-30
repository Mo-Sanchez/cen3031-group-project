from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from wtforms.fields import TimeField, BooleanField, HiddenField
from datetime import datetime
from UserCreator import UserCreator
from UserLogin import UserLogin
from db import db
from meetings import MeetingCreator
from datetime import datetime, timedelta
from bson import ObjectId
from flask import jsonify
from UserInstance import UserInstance


def current_user_email():
    return session.get('email')


def current_user_name():
    return session.get('name')


def half_hour_choices():
    return [(f"{h:02d}:{m:02d}", f"{h:02d}:{m:02d}")
            for h in range(24) for m in (0, 30)]


app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-to-a-very-secret-key'

# MOCK USER DB
mock_users = {
    'student@demo.com': {
        'name': 'Lucas',
        'role': 'Student'
    },
    'tutor@demo.com': {
        'name': 'Bond',
        'role': 'Tutor',
        'availability': {'start': '09:00', 'end': '17:00'}
    },
    'smith@demo.com': {
        'name': 'Smith',
        'role': 'Tutor',
        'availability': {'start': '10:00', 'end': '16:00'}
    }
}

# MOCK APPOINTMENTS
tutor_appointments = {
    'Bond': [
        {'date': '2025-07-15', 'time': '10:00'},
        {'date': '2025-07-18', 'time': '13:00'}
    ],
    'Smith': []
}


# FORMS
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Account Type', choices=[('Student', 'Student'), ('Tutor', 'Tutor')], validators=[DataRequired()])
    subject = StringField('Subject', validators=[Optional()])
    start_avail = SelectField('Start Availability', choices=half_hour_choices(), validators=[Optional()])
    end_avail = SelectField('End Availability', choices=half_hour_choices(), validators=[Optional()])

    submit = SubmitField('Register')


class AccountSettingsForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Save')
    delete = HiddenField(
        'data',
        render_kw={'id': 'data'},
        default="None"
    )


class AvailabilityForm(FlaskForm):
    start = TimeField('Start Time', format='%H:%M', validators=[DataRequired()])
    end = TimeField('End Time', format='%H:%M', validators=[DataRequired()])
    submit = SubmitField('Update Availability')


# ---- ROUTES ----

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    login = UserLogin()

    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        print("Debug: About to Login")
        user_doc = login.login(email, password)
        print("Debug: Logged In")

        if user_doc:
            userName = user_doc["name"]
            userEmail = user_doc["email"]
            userRole = user_doc["role"]

            loggedInUser = {
                'name': userName,
                'role': userRole
            }

            session['role'] = userRole
            session['name'] = userName
            session['user'] = loggedInUser
            session['email'] = userEmail

            return redirect(url_for(f"{userRole.lower()}_dashboard"))

        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    creator = UserCreator()
    form = RegistrationForm()
    success = False
    message = ""
    if form.validate_on_submit():
        email = form.email.data.lower()

        role = form.role.data

        if role == "Student":
            success, message = creator.create_student_user(
                form.name.data,
                email,
                form.password.data,
                form.role.data
            )

        # For tutors, default availability
        # user = {'name': email.split('@')[0].capitalize(), 'role': role}

        if role == 'Tutor':
            success, message = creator.create_tutor_user(
                form.name.data,
                email,
                form.password.data,
                form.role.data,
                form.subject.data,
                form.start_avail.data,
                form.end_avail.data
            )
        if success:
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        else:
            flash("Error: user already exists!", "error")
            return redirect(url_for('register'))

    return render_template('register.html', form=form)


@app.route('/student_dashboard')
@app.route('/student_dashboard')
def student_dashboard():
    if session.get('role') != 'Student':
        flash("Please log in as student.", "warning")
        return redirect(url_for('login'))

    meetings_coll = db["meetings"]
    users_coll    = db["users"]
    student_email = session["email"]

    meetings = meetings_coll.find({"studentEmail": student_email})

    appointments = []
    for m in meetings:
        tutor_doc = users_coll.find_one({"email": m["tutorEmail"]}, {"name": 1})
        appointments.append({
            "id":   str(m["_id"]),                       # ←  add this
            "date": m["scheduledDate"],
            "time": m["scheduledTime"],
            "tutor": tutor_doc["name"] if tutor_doc else m["tutorEmail"],
            "subject": m.get("subject", "N/A")
        })

    return render_template(
        'student_dashboard.html',
        student_name=session["name"],
        appointments=appointments
    )


@app.route('/tutor_dashboard')
def tutor_dashboard():
    if session.get('role') != 'Tutor':
        flash("Please log in as tutor.", "warning")
        return redirect(url_for('login'))

    tutor_email = session["email"]
    booked      = db["meetings"].find({"tutorEmail": tutor_email})

    appointments = []
    for m in booked:
        appointments.append({
            "id":      str(m["_id"]),
            "date":    m["scheduledDate"],
            "time":    m["scheduledTime"],
            "student": m["studentEmail"],
            "subject": m["subject"]
        })

    return render_template(
        'tutor_dashboard.html',
        tutor_name=session["name"],
        appointments=appointments
    )


@app.route('/settings', methods=['GET', 'POST'])
def account_settings():
    creator = UserCreator()
    form = AccountSettingsForm()
    user = session.get("user", {})

    if request.method == "GET":
        form.name.data = user.get("name", "")

    if form.validate_on_submit():
        if form.delete.data == "True":
            # user deletes account
            creator.delete_by_email([current_user_email()])
            flash("Account successfully deleted.", "success")
            return redirect(url_for('register'))
        elif form.delete.data != "False":
            user['name'] = form.name.data
            session['name'] = form.name.data
            session['user'] = user
            creator.change_name(session['email'], form.name.data)
            flash("Name updated!", "success")
        return redirect(url_for('account_settings'))

    return render_template('settings.html', form=form, user=user)


@app.route('/availability_settings', methods=['GET', 'POST'])
def availability_settings():
    if session.get('role') != 'Tutor':
        flash("Only tutors can edit availability.", "danger")
        return redirect(url_for('login'))

    users = db["users"]
    email = session["email"]
    tutor = users.find_one({"email": email, "role": "Tutor"})
    if not tutor:
        flash("Tutor not found.", "danger")
        return redirect(url_for('tutor_dashboard'))

    form = AvailabilityForm()

    if request.method == "GET":
        form.start.data = datetime.strptime(tutor["start_availability"], '%H:%M').time()
        form.end.data   = datetime.strptime(tutor["end_availability"],   '%H:%M').time()

    if form.validate_on_submit():
        start = form.start.data.strftime('%H:%M')
        end   = form.end.data.strftime('%H:%M')

        if start >= end:
            flash("End time must be after start time.", "danger")
            return render_template('availability_settings.html', form=form)

        users.update_one(
            {"email": email},
            {"$set": {
                "start_availability": start,
                "end_availability":   end
            }}
        )
        flash("Availability updated!", "success")
        return redirect(url_for('tutor_dashboard'))

    return render_template('availability_settings.html', form=form, tutor_name=session["name"])



@app.route('/make_appointment', methods=['GET', 'POST'])
def make_appointment():
    # only students can book
    if session.get('role') != 'Student':
        flash("Please log in as a student.", "warning")
        return redirect(url_for('login'))

    users_coll     = db["users"]
    meetings_coll  = db["meetings"]
    # only tutors that have start & end availability
    tutors_docs = list(
        users_coll.find(
            {
                "role": "Tutor",
                "start_availability": {"$exists": True, "$type": "string", "$ne": ""},
                "end_availability":   {"$exists": True, "$type": "string", "$ne": ""}
            },
            {
                "_id": 0,
                "name": 1,
                "email": 1,
                "start_availability": 1,
                "end_availability": 1
            }
        )
    )

    tutors_map = {t["email"]: t for t in tutors_docs}

    if request.method == "POST":
        date_str    = request.form["date"]
        time_str    = request.form["time"]
        tutor_email = request.form["tutor"]
        subject     = request.form["subject"]

        tutor_doc = tutors_map.get(tutor_email)
        if not tutor_doc:
            flash("Tutor not found.", "danger")
            return render_template(
                "make_appointment.html",
                tutors=tutors_docs
            )

        # availability check
        start = tutor_doc.get("start_availability")
        end   = tutor_doc.get("end_availability")
        if not (start and end and start <= time_str <= end):
            flash(
                f"{tutor_doc['name']} is available only between "
                f"{start} and {end}.",
                "danger"
            )
            return render_template(
                "make_appointment.html",
                tutors=tutors_docs
            )

        # conflict check
        clash = meetings_coll.find_one({
            "tutorEmail": tutor_email,
            "scheduledDate": date_str,
            "scheduledTime": time_str
        })
        if clash:
            flash(
                f"{tutor_doc['name']} already has an appointment at that time.",
                "danger"
            )
            return render_template(
                "make_appointment.html",
                tutors=tutors_docs
            )

        # create meeting
        creator = MeetingCreator()
        creator.create_meeting(
            tutor_email     = tutor_email,
            student_email   = session["email"],
            scheduled_date  = date_str,
            scheduled_time  = time_str,
            subject         = subject
        )

        flash(
            f"Appointment booked for {date_str} at {time_str} with "
            f"{tutor_doc['name']} ({subject}).",
            "success"
        )
        return redirect(url_for("student_dashboard"))

    # GET request
    return render_template("make_appointment.html", tutors=tutors_docs)


@app.route('/cancel_appointment', methods=['POST'])
def cancel_appointment():
    role  = session.get('role')
    email = session.get('email')
    meet_id = request.form.get('meeting_id')

    if role not in ("Student", "Tutor") or not meet_id:
        flash("Invalid request.", "danger")
        return redirect(url_for('index'))

    criteria = {"_id": ObjectId(meet_id)}
    if role == "Student":
        criteria["studentEmail"] = email
    else:
        criteria["tutorEmail"] = email

    deleted = db["meetings"].delete_one(criteria).deleted_count
    flash("Appointment cancelled." if deleted else "Appointment not found.",
          "success" if deleted else "danger")

    return redirect(url_for(f"{role.lower()}_dashboard"))


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
