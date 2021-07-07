from flask import Blueprint, render_template, request, url_for, redirect, flash, jsonify, current_app
from abac.admin.models import Admin
from abac.patients.models import Patient
from abac.workers.models import Worker
from abac.workers.utils import worker_login_required, worker_already_logged_in
import json
import textwrap
from bson.json_util import dumps, loads
from rsb import generateCipher

# attaching the patients blueprint
workers = Blueprint('workers', __name__)


# the signin route
@workers.get('/signin/')
@worker_already_logged_in
def signin():
    url = '/workers/signin/'
    return render_template('patients/worker_login.html', url=url)


# the signin post route
@workers.post('/signin/')
@worker_already_logged_in
def login():
    # handling form validation
    form = request.form
    data = {
        "identifier": form['email'],
        "password": form["password"]
    }
    user = Worker().signin(data)

    if user == False:
        flash('Invalid Signin Details', "danger")
        return redirect(url_for('workers.signin'))
    else:
        # flash(f'Welcome back', "success")
        return redirect(url_for('workers.dashboard'))


# the signout route
@workers.get('/signout/')
@worker_login_required
def logout(user):
    response = Worker.signout()
    if response:
        return redirect(url_for('main.home'))


# the worker dashboard route
@workers.get('/dashboard/')
@worker_login_required
def dashboard(user):
    # getting the workers and patient count
    doctors = Admin.get_workers('doctor').count()
    pharmacists = Admin.get_workers('pharmacist').count()
    nurses = Admin.get_workers('nurse').count()
    patients_c = Patient.get_patients().count()
    data = {
        "dc": doctors,
        "pc": pharmacists,
        "nc": nurses,
        "pac": patients_c
    }
    # getting the hospital staff
    patients = Patient.get_patients()

    return render_template('patients2/dashboard-w.html', user=user, data=data, patients=patients)


# the patient public profile
@workers.get('/patients/profile/')
@worker_login_required
def patientProfile(user):
    # getting the patient id
    id = request.args.get('id')
    patient = Patient.get_user(id)
    return render_template('patients2/profile_new_2.html', patient=patient, user=user)


# the list patients route
@workers.get('/patients/list/')
@worker_login_required
def listPatients(user):
    patients = Patient.get_patients()

    return render_template('patients2/patient-list-w.html', user=user, patients=patients)


# the retrieve record categories route
@workers.get('/patients/records/')
@worker_login_required
def getRecord(user):
    # getting the query parameters
    id = request.args.get('id')
    # getting the patient
    patient = Patient.get_user(id)

    # instantiating the encryption algorithm
    key = current_app.config['SECRET_KEY'].encode()
    gc = generateCipher(key)

    mp = Patient.get_mp(user['public_id'])
    vi = Patient.get_vi(user['public_id'])
    dt = Patient.get_dt(user['public_id'])

    return render_template('patients2/select-record-w.html', user=user, patient=patient)


# the view records route
@workers.get('/patients/view/')
@worker_login_required
def viewRecord(user):
    # getting the query parameters
    id = request.args.get('id')
    data = request.args.get('data')
    # getting the patient
    patient = Patient.get_user(id)

    # instantiating the encryption algorithm
    key = current_app.config['SECRET_KEY'].encode()
    gc = generateCipher(key)

    """
    Returning data based on health record type
    mp ---- medicine prescriptions
    vi ---- vitals
    dt ---- diagnostic tests
    """
    if data == 'mp':
        view = 'Medicine Prescriptions'
        records = Patient.get_mp(id)
        if records:
            records = Patient.get_mp(id)['record']
            policy = gc.decode(records)['policy']
            records = gc.decode(records)['record']
    elif data == 'vi':
        view = 'Vitals'
        records = Patient.get_vi(id)
        if records:
            records = Patient.get_vi(id)['record']
            policy = gc.decode(records)['policy']
            records = gc.decode(records)['record']
    elif data == 'dt':
        view = 'Recommended Diagnostic Tests'
        records = Patient.get_dt(id)
        if records:
            records = Patient.get_dt(id)['record']
            policy = gc.decode(records)['policy']
            records = gc.decode(records)['record']

    return render_template('patients2/data-table.html', user=user, patient=patient, view=view, data=data, records=records, json=json, gc=gc)
