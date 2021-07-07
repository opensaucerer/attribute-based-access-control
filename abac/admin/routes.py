from flask import Blueprint, render_template, request, url_for, redirect, flash
from abac.admin.models import Admin
from abac.patients.models import Patient
from abac.admin.utils import admin_login_required, admin_already_logged_in
import json
import textwrap
from bson.json_util import dumps, loads

# attaching the patients blueprint
admin = Blueprint('admin', __name__)


# the signin route
@admin.get('/signin/')
@admin_already_logged_in
def signin():
    url = '/admin/signin/'
    return render_template('patients/admin_login.html', url=url)


# the signin post route
@admin.post('/signin/')
@admin_already_logged_in
def login():
    # handling form validation
    form = request.form
    data = {
        "identifier": form['email'],
        "password": form["password"]
    }
    user = Admin().signin(data)

    if user == False:
        flash('Invalid Signin Details', "danger")
        return redirect(url_for('admin.signin'))
    else:
        # flash(f'Welcome back', "success")
        return redirect(url_for('admin.dashboard'))


# the signout route
@admin.get('/signout/')
@admin_login_required
def logout(user):
    response = Admin.signout()
    if response:
        return redirect(url_for('main.home'))


# the admin dashboard route
@admin.get('/dashboard/')
@admin_login_required
def dashboard(user):
    # getting the workers and patient count
    doctors = Admin.get_workers('doctor').count()
    pharmacists = Admin.get_workers('pharmacist').count()
    nurses = Admin.get_workers('nurse').count()
    patients = Patient.get_patients().count()
    data = {
        "dc": doctors,
        "pc": pharmacists,
        "nc": nurses,
        "pac": patients
    }
    # getting the hospital staff
    workers = Admin.get_workers()

    return render_template('patients2/dashboard-1.html', user=user, data=data, workers=workers)


# the hospital stats route
@admin.get('/stats/')
@admin_login_required
def stats(user):
    return render_template('patients2/dashboard-2.html', user=user)


# the add worker route
@admin.get('/workers/add/')
@admin_login_required
def getAddWorker(user):
    url = '/admin/workers/add/'
    return render_template('patients2/add-doctor.html', user=user, url=url)


# the add worker post route
@admin.post('/workers/add/')
@admin_login_required
def addWorker(user):
    url = '/admin/workers/add/'
    # handling form validation
    form = request.form
    # collecting form data
    form = request.form
    fname = form['fname']
    lname = form['lname']
    email = form['email']
    password = form['password']
    re_password = form['re_password']
    address = form['address']
    number = form['number']
    gender = form['gender']
    role = form['role']
    errors = {}

    # handling form validation
    if password != re_password:
        errors['password'] = 'Passwords do not match'
    if Admin.check_email(email):
        errors['email'] = 'That email is already in use'
    if Admin.check_number(number):
        errors['number'] = 'That phone number is already in use'

    if len(errors) > 0:
        return render_template('patients2/add-doctor.html', user=user, url=url, errors=errors)

    worker = Admin(fname, lname, email, password,
                   address, number, gender, role)
    worker.register()

    return redirect(url_for('admin.listWorkers'))


# the list workers route
@admin.get('/workers/list/')
@admin_login_required
def listWorkers(user):
    workers = Admin.get_workers()

    return render_template('patients2/doctor-list.html', user=user, workers=workers)


# the list patients route
@admin.get('/patients/list/')
@admin_login_required
def listPatients(user):
    patients = Patient.get_patients()

    return render_template('patients2/patient-list.html', user=user, patients=patients)


# the retrieve record categories route
@admin.get('/patients/records/')
@admin_login_required
def getRecord(user):
    # getting the query parameters
    id = request.args.get('id')
    # getting the patient
    patient = Patient.get_user(id)

    return render_template('patients2/select-record.html', user=user, patient=patient)


# the view records route
@admin.get('/patients/view/')
@admin_login_required
def viewRecord(user):
    # getting the query parameters
    id = request.args.get('id')
    data = request.args.get('data')
    # getting the patient
    patient = Patient.get_user(id)

    """
    Returning data based on health record type
    mp ---- medicine prescriptions
    vi ---- vitals
    dt ---- diagnostic tests
    """

    if data == 'mp':
        view = 'Medicine Prescriptions'
        records = Patient.get_mp(id)
    elif data == 'vi':
        records = Patient.get_vi(id)
        view = 'Vitals'
    elif data == 'dt':
        records = Patient.get_dt(id)
        view = 'Recommended Diagnostic Tests'

    return render_template('patients2/data-table.html', user=user, patient=patient, view=view, data=data, records=records, json=json)


# the edit records route
@admin.get('/patients/edit/')
@admin_login_required
def editRecord(user):
    # getting the query parameters
    id = request.args.get('id')
    data = request.args.get('data')
    # getting the patient
    patient = Patient.get_user(id)
    # getting the workers
    workers = Admin.get_workers()

    """
    Returning data based on health record type
    mp ---- medicine prescriptions
    vi ---- vitals
    dt ---- diagnostic tests
    
    """

    if data == 'mp':
        view = 'Medicine Prescriptions'
        records = Patient.get_mp(id)
    elif data == 'vi':
        records = Patient.get_vi(id)
        view = 'Vitals'
    elif data == 'dt':
        records = Patient.get_dt(id)
        view = 'Recommended Diagnostic Tests'

    return render_template('patients2/table-editable.html', user=user, workers=workers, patient=patient, view=view, data=data, records=records, json=json)
