from flask import session

def current_user_email():
    return session.get('email')


def current_user_name():
    return session.get('name')