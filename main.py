from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from wtforms.fields import TimeField
from datetime import datetime


def current_user_email():
    return session.get('email')

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
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Account Type', choices=[('Student', 'Student'), ('Tutor', 'Tutor')], validators=[DataRequired()])
    submit = SubmitField('Register')

class AccountSettingsForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Save')

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
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        # Demo passwords:
        #   student@demo.com / student123
        #   tutor@demo.com / tutor123
        #   smith@demo.com / smith123
        if email in mock_users:
            role = mock_users[email]['role']
            # Demo check: student123, tutor123, smith123
            if (role == 'Student' and password == 'student123') or \
               (email == 'tutor@demo.com' and password == 'tutor123') or \
               (email == 'smith@demo.com' and password == 'smith123'):
                session['role'] = role
                session['user'] = mock_users[email]['name']
                session['email'] = email
                return redirect(url_for(f"{role.lower()}_dashboard"))
            else:
                flash("Invalid credentials", "danger")
        else:
            flash("User not found", "danger")
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        if email in mock_users:
            flash("User already exists.", "danger")
            return render_template('register.html', form=form)
        role = form.role.data

        # For tutors, default availability
        user = {'name': email.split('@')[0].capitalize(), 'role': role}

        if role == 'Tutor':
            user['availability'] = {'start': '09:00', 'end': '17:00'}
        mock_users[email] = user
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/student_dashboard')
def student_dashboard():
    if session.get('role') != 'Student':
        flash("Please log in as student.", "warning")
        return redirect(url_for('login'))
    # List all tutors for new appointment, and sample appointment display
    appointments = []
    for tutor, apps in tutor_appointments.items():
        for a in apps:
            appointments.append({'date': a['date'], 'time': a['time'], 'tutor': tutor, 'subject': 'Demo'})
    return render_template('student_dashboard.html', student_name=session.get('user', ''), appointments=appointments)

@app.route('/tutor_dashboard')
def tutor_dashboard():
    if session.get('role') != 'Tutor':
        flash("Please log in as tutor.", "warning")
        return redirect(url_for('login'))
    tutor_name = session.get('user', '')
    appointments = tutor_appointments.get(tutor_name, [])
    # Display booked times
    display = []
    for a in appointments:
        display.append({'date': a['date'], 'time': a['time'], 'student': 'Student', 'subject': 'Demo'})
    return render_template('tutor_dashboard.html', tutor_name=tutor_name, appointments=display)

@app.route('/settings', methods=['GET', 'POST'])
def account_settings():
    email = current_user_email()
    if not email or email not in mock_users:
        flash("Please log in.", "warning")
        return redirect(url_for('login'))

    form = AccountSettingsForm()
    user = mock_users[email]
    if request.method == 'GET':
        form.name.data = user.get('name', '')

    if form.validate_on_submit():
        user['name'] = form.name.data
        session['user'] = form.name.data  # Update session display
        flash("Name updated!", "success")
        return redirect(url_for('account_settings'))
    return render_template('settings.html', form=form, user=user)

@app.route('/tutor/settings', methods=['GET', 'POST'])
def tutor_settings():
    email = current_user_email()
    if not email or mock_users.get(email, {}).get('role') != 'Tutor':
        flash("Only tutors can set availability.", "danger")
        return redirect(url_for('login'))

    tutor_name = mock_users[email]['name']
    form = AvailabilityForm()
    avail = mock_users[email]['availability']
    # Pre-populate with current values on GET
    if request.method == 'GET':
        form.start.data = datetime.strptime(avail['start'], '%H:%M').time()
        form.end.data = datetime.strptime(avail['end'], '%H:%M').time()

    if form.validate_on_submit():
        avail['start'] = form.start.data.strftime('%H:%M')
        avail['end'] = form.end.data.strftime('%H:%M')
        flash('Availability updated!', 'success')
        return redirect(url_for('tutor_settings'))

    return render_template('tutor_settings.html', form=form, tutor_name=tutor_name)

@app.route('/make_appointment', methods=['GET', 'POST'])
def make_appointment():
    if session.get('role') != 'Student':
        flash("Please log in as student.", "warning")
        return redirect(url_for('login'))

    tutors = [email for email, u in mock_users.items() if u['role'] == 'Tutor']

    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        tutor_email = request.form['tutor']
        subject = request.form['subject']

        tutor_user = mock_users[tutor_email]
        tutor_name = tutor_user['name']
        start = tutor_user['availability']['start']
        end = tutor_user['availability']['end']
        if not (start <= time <= end):
            flash(f"{tutor_name} is only available between {start} and {end}.", 'danger')
            return render_template('make_appointment.html', tutors=tutors, mock_users=mock_users)

        # Check for conflicts
        appts = tutor_appointments.setdefault(tutor_name, [])
        conflict = any(app['date'] == date and app['time'] == time for app in appts)
        if conflict:
            flash(f"{tutor_name} already has an appointment at this time. Please pick another slot.", 'danger')
            return render_template('make_appointment.html', tutors=tutors, mock_users=mock_users)

        # Otherwise, book it
        appts.append({'date': date, 'time': time})
        flash(f'Appointment booked for {date} at {time} with {tutor_name} for {subject}.', 'success')
        return redirect(url_for('student_dashboard'))

    return render_template('make_appointment.html', tutors=tutors, mock_users=mock_users)

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
