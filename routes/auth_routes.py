from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from models.user_login import UserLogin
from models.user_creator import UserCreator
from forms.login_form import LoginForm
from forms.register_form import RegistrationForm

auth_bp = Blueprint('auth_bp', __name__)


# Displays and handles login form submission, verifies user credentials, starts session, and redirects based on user role
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form  = LoginForm()
    auth  = UserLogin()

    if form.validate_on_submit():
        user = auth.login(form.email.data.lower(), form.password.data)
        if not user:
            flash("Invalid credentials", "danger")
        else:
            session.clear()
            session.update({
                "email": user["email"],
                "name":  user["name"],
                "role":  user["role"]
            })

            session["user"] = {"name": user["name"], "role": user["role"]}

            role_endpoint = {
                "Student": "student_bp.student_dashboard",
                "Tutor":   "tutor_bp.tutor_dashboard"
            }
            return redirect(url_for(role_endpoint[user["role"]]))

    return render_template('login.html', form=form)




# Displays registration form and creates a new Student/Tutor account based on role selected
@auth_bp.route('/register', methods=['GET', 'POST'], endpoint='register')
def register():
    creator = UserCreator()
    form    = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        role  = form.role.data

        if role == "Student":
            ok, msg = creator.create_student_user(
                form.name.data, email, form.password.data, role)
        else:  # Tutor
            ok, msg = creator.create_tutor_user(
                form.name.data, email, form.password.data, role,
                form.subject.data, form.start_avail.data, form.end_avail.data)

        if ok:
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('auth_bp.login'))
        else:
            flash(msg, "danger")
            return redirect(url_for('auth_bp.register'))

    return render_template('register.html', form=form)

#Logs out
@auth_bp.route('/logout',endpoint='logout')
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for('index'))