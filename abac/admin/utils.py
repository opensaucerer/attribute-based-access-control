# importing modules
from functools import wraps
from flask import session, flash, redirect, url_for, request, jsonify
from abac.admin.models import Admin


# login in required decorator
def admin_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_user' in session:
            if session['admin_authenticated'] and "admin_user" in session:
                user = session['admin_user']

        else:
            flash('You must be an admin to access that page', 'danger')
            return redirect(url_for('admin.signin'))

        return f(user, *args, **kwargs)

    return decorated


# already logged in decorator
def admin_already_logged_in(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_user' in session:
            if session['admin_authenticated'] and "admin_user" in session:
                user = session['admin_user']
                return redirect(url_for('admin.dashboard'))

        return f(*args, **kwargs)

    return decorated
