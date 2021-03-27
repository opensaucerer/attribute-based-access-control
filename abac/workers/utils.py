# importing modules
from functools import wraps
from flask import session, flash, redirect, url_for, request, jsonify
from abac.workers.models import Worker


# login in required decorator
def worker_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'worker_user' in session:
            if session['worker_authenticated'] and "worker_user" in session:
                user = session['worker_user']

        else:
            flash('You must be an admin to access that page', 'danger')
            return redirect(url_for('workers.signin'))

        return f(user, *args, **kwargs)

    return decorated


# already logged in decorator
def worker_already_logged_in(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'worker_user' in session:
            if session['worker_authenticated'] and "worker_user" in session:
                user = session['worker_user']
                return redirect(url_for('workers.dashboard'))

        return f(*args, **kwargs)

    return decorated
