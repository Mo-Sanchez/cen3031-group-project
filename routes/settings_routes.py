from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from models.user_creator import UserCreator
from forms.account_settings_form import AccountSettingsForm
from routes.__init__ import current_user_email

settings_bp = Blueprint('settings_bp', __name__)


# Displays account settings form, handles name changes or account deletion, and updates the session and database accordingly
@settings_bp.route('/settings', methods=['GET', 'POST'])
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
            return redirect(url_for('auth_bp.register'))
        elif form.delete.data != "False":
            user['name'] = form.name.data
            session['name'] = form.name.data
            session['user'] = user
            creator.change_name(session['email'], form.name.data)
            flash("Name updated!", "success")
        return redirect(url_for('settings_bp.account_settings'))

    return render_template('settings.html', form=form, user=user)