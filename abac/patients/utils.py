# importing modules
from functools import wraps
from flask import session, flash, redirect, url_for, request, jsonify
from abac.patients.models import Patient


# login in required decorator
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'current_user' in session:
            if session['is_authenticated'] and "current_user" in session:
                user = session['current_user']

        else:
            flash('You must be signed in to access that page', 'danger')
            return redirect(url_for('patients.signin'))

        return f(user, *args, **kwargs)

    return decorated


# already logged in decorator
def already_logged_in(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'current_user' in session:
            if session['is_authenticated'] and "current_user" in session:
                user = session['current_user']
                return redirect(url_for('patients.dashboard'))

        return f(*args, **kwargs)

    return decorated
