from flask import Blueprint, render_template, redirect, url_for, flash, session, request


demo_bp = Blueprint('demo_bp', __name__)


# Shows one dummy past meeting.
@demo_bp.route('/demo_rate', methods=['GET', 'POST'])
def demo_rate():


    if request.method == 'POST':
        rating  = request.form['rating']
        comment = request.form.get('comment', '')
        flash(f"Thanks! You rated Bruce Wayne {rating}/5 – {comment}", "success")
        return redirect(url_for('demo_rate'))

    # one dummy meeting row
    past_meetings = [{
        "_id": "demo-001",
        "tutor_name": "Bruce Wayne",
        "scheduled_time": "2025-07-01 10:00 AM"
    }]

    return render_template("rate_tutor.html", past_meetings=past_meetings)