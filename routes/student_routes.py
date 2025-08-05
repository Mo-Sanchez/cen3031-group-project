from flask import Blueprint, render_template, redirect, url_for, flash, session
from db import db
from bson import ObjectId
from flask import request
from models.meetings import MeetingCreator

student_bp = Blueprint('student_bp', __name__)

# Displays current student appoints, and pulls meeting data by studentEmail and shows tutor name and subject

@student_bp.route('/student_dashboard', endpoint='student_dashboard')
def student_dashboard():
    # role check (redirect if not a student)
    if session.get('role') != 'Student':
        flash("Please log in as a student.", "warning")
        return redirect(url_for('auth_bp.login'))

    meetings = db.meetings.find({"studentEmail": session['email']})
    users    = db.users

    appointments = [{
        "id":   str(m["_id"]),
        "date": m["scheduledDate"],
        "time": m["scheduledTime"],
        "tutor": users.find_one({"email": m["tutorEmail"]}, {"name": 1})["name"]
                 if users.find_one({"email": m["tutorEmail"]}) else m["tutorEmail"],
        "subject": m.get("subject", "N/A")
    } for m in meetings]

    return render_template(
        'student_dashboard.html',
        student_name=session['name'],
        appointments=appointments
    )


# GET: Renders form with all available tutors
# POST: If only dat and subject are submitted, shows matching tutors with availability
# if time is also submitted, performs availability and clash checks and books the meeting
@student_bp.route('/make_appointment', methods=['GET', 'POST'], endpoint='make_appointment')
def make_appointment():
    if session.get('role') != 'Student':
        flash("Please log in as a student.", "warning")
        return redirect(url_for('auth_bp.login'))

    users_coll    = db.users
    meetings_coll = db.meetings
    creator       = MeetingCreator()

    # Grab tutors that actually have availability set
    tutors_docs = list(users_coll.find(
        {
            "role": "Tutor",
            "start_availability": {"$exists": True, "$type": "string", "$ne": ""},
            "end_availability":   {"$exists": True, "$type": "string", "$ne": ""}
        },
        {"_id":0, "name":1, "email":1, "start_availability":1, "end_availability":1}
    ))
    tutors_map = {t["email"]: t for t in tutors_docs}

    # ─────────────── POST ───────────────
    if request.method == "POST":
        # SEARCH phase (no time yet)
        if not request.form.get("time"):
            date_str     = request.form["date"]
            subject      = request.form["subject"]
            tutor_filter = request.form.get("tutor_filter", "").strip()

            matching = (creator.search_by_date_and_subject(date_str, subject, tutor_filter)
                        if tutor_filter else
                        creator.search_by_date_and_subject(date_str, subject))

            # add extra fields
            for t in matching:
                full  = users_coll.find_one({"email": t["email"]})
                t["subjects"] = full.get("subjects", [])

                ratings = [m["rating"] for m in meetings_coll.find({
                              "tutorEmail": t["email"], "rating": {"$exists": True}})
                           if isinstance(m.get("rating"), (int,float))]
                t["avg_rating"] = round(sum(ratings)/len(ratings),2) if ratings else None

            return render_template("search_results.html",
                                   tutors=matching, date=date_str, subject=subject)

        # BOOKING phase (time present)
        date_str    = request.form["date"]
        time_str    = request.form["time"]
        tutor_email = request.form["tutor"]
        subject     = request.form["subject"]

        tutor_doc = tutors_map.get(tutor_email)
        if not tutor_doc:
            flash("Tutor not found.", "danger")
            return render_template("make_appointment.html", tutors=tutors_docs)

        # availability window check
        start, end = tutor_doc["start_availability"], tutor_doc["end_availability"]
        if not (start <= time_str <= end):
            flash(f"{tutor_doc['name']} is available only between {start} and {end}.", "danger")
            return render_template("make_appointment.html", tutors=tutors_docs)

        # clash check
        clash = meetings_coll.find_one({
            "tutorEmail": tutor_email,
            "scheduledDate": date_str,
            "scheduledTime": time_str
        })
        if clash:
            flash(f"{tutor_doc['name']} already has an appointment at that time.", "danger")
            return render_template("make_appointment.html", tutors=tutors_docs)

        # create
        creator.create_meeting(tutor_email, session["email"], date_str, time_str, subject)
        flash(f"Appointment booked for {date_str} at {time_str} with {tutor_doc['name']} ({subject}).",
              "success")
        return redirect(url_for('student_bp.student_dashboard'))

    # ─────────────── GET ───────────────
    return render_template("make_appointment.html", tutors=tutors_docs)


# GET: Shows past meetings to rate
# POST: Allows student to rate a tutor and optionally leave a comment
@student_bp.route('/rate_tutor', methods=['GET', 'POST'], endpoint='rate_tutor')
def rate_tutor():
    if session.get('role') != 'Student':
        flash("Access denied.", "danger")
        return redirect(url_for('auth_bp.login'))

    meetings_coll = db.meetings
    users_coll    = db.users
    creator       = MeetingCreator()


    if request.method == "POST":
        meeting_id = request.form["meeting_id"]
        rating = int(request.form["rating"])
        comment = request.form.get("comment", "")

        if ObjectId.is_valid(meeting_id):
            msg = creator.update_rating(meeting_id, rating, comment)
            flash(msg, "success" if msg == "Rating updated" else "danger")
        else:
            flash("Demo rating received — not stored in database.", "info")

        return redirect(url_for('student_bp.rate_tutor'))

    real = list(meetings_coll.find({"studentEmail": session['email']}))
    past_meetings = [{
        "_id": str(m["_id"]),
        "tutor_name": users_coll.find_one({"email": m["tutorEmail"]})["name"],
        "scheduled_time": f"{m['scheduledDate']} {m['scheduledTime']}"
    } for m in real]

    # demo row if the student has no past meetings
    if not past_meetings:
        past_meetings.append({
            "_id": "demo-001",
            "tutor_name": "Bruce Wayne",
            "scheduled_time": "2025-07-01 10:00 AM"
        })

    return render_template('rate_tutor.html', past_meetings=past_meetings)


@student_bp.route('/cancel_appointment', methods=['POST'], endpoint='cancel_appointment')
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

    deleted = db.meetings.delete_one(criteria).deleted_count
    flash("Appointment cancelled." if deleted else "Appointment not found.",
          "success" if deleted else "danger")

    # redirect back to the appropriate dashboard
    return redirect(url_for(f"{'student_bp.student_dashboard' if role=='Student' else 'tutor_bp.tutor_dashboard'}"))



@student_bp.route('/select_time')
def select_time():
    creator     = MeetingCreator()
    tutor_email = request.args.get("tutor")
    date        = request.args.get("date")
    subject     = request.args.get("subject")

    users_coll  = db["users"]
    tutor_doc   = users_coll.find_one({"email": tutor_email})

    if not tutor_doc:
        flash("Tutor not found.", "danger")
        return redirect(url_for('student_bp.make_appointment'))

    available_times = creator.get_available_times(date, tutor_email)

    return render_template(
        "select_time.html",
        tutor=tutor_doc,
        date=date,
        subject=subject,
        available_times=available_times
    )


@student_bp.route('/tutor_profile/<email>')
def tutor_profile(email):
    users_coll = db['users']
    meetings_coll = db['meetings']

    tutor = users_coll.find_one({"email": email})
    if not tutor:
        flash("Tutor not found.", "danger")
        return redirect(url_for("make_appointment"))

    # Gather all ratings from past meetings
    meetings = list(meetings_coll.find({
        "tutorEmail": email,
        "rating": {"$exists": True}
    }))

    ratings = [m["rating"] for m in meetings if isinstance(m.get("rating"), (int, float))]
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None

    return render_template("tutor_profile.html", tutor=tutor, avg_rating=avg_rating)