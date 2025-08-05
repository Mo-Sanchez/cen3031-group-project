from flask import Blueprint, render_template, redirect, url_for, flash, session
from forms.availability import AvailabilityForm

from db import db
from flask import request
from datetime import datetime

tutor_bp = Blueprint('tutor_bp', __name__)

# Displays tutor scheduled meeting, including student email and subject
@tutor_bp.route('/tutor_dashboard', endpoint='tutor_dashboard')
def tutor_dashboard():
    if session.get('role') != 'Tutor':
        flash("Please log in as a tutor.", "warning")
        return redirect(url_for('auth_bp.login'))

    meetings = db.meetings.find({"tutorEmail": session['email']})
    appointments = [{
        "id":      str(m["_id"]),
        "date":    m["scheduledDate"],
        "time":    m["scheduledTime"],
        "student": m["studentEmail"],
        "subject": m["subject"]
    } for m in meetings]

    return render_template(
        'tutor_dashboard.html',
        tutor_name=session['name'],
        appointments=appointments
    )



# GET: Prefills the avilability form with the current availability
# POST: Validates and updates the tutors start and end availability in the database, ensuring the end time is after the start time
@tutor_bp.route('/availability_settings', methods=['GET', 'POST'], endpoint='availability_settings')
def availability_settings():
    if session.get('role') != 'Tutor':
        flash("Only tutors can edit availability.", "danger")
        return redirect(url_for('auth_bp.login'))

    users = db.users
    email = session['email']
    tutor = users.find_one({"email": email, "role": "Tutor"})
    if not tutor:
        flash("Tutor not found.", "danger")
        return redirect(url_for('tutor_bp.tutor_dashboard'))

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
            {"$set": {"start_availability": start, "end_availability": end}}
        )
        flash("Availability updated!", "success")
        return redirect(url_for('tutor_bp.tutor_dashboard'))

    return render_template('availability_settings.html',
                           form=form, tutor_name=session['name'])
