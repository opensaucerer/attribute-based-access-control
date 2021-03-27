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


# the patient profile edit route
@workers.get('/edit_profile/')
@worker_login_required
def editProfile(user):
    url = '/workers/edit_profile/'
    return render_template('patients2/worker_edit.html', user=user, worker=user)


# the patient profile edit POST route
@workers.post('/edit_profile/')
@worker_login_required
def postEditProfile(user):
    # collecting form data
    form = request.form
    data = {
        "fname": form['fname'],
        "lname": form['lname'],
        "email": form['email'],
        "address": form['address'],
        "number": form['number'],
        "gender": form['gender'],
    }

    try:
        user = user['public_id']
        response = Worker().update_profile(user, data)
        return redirect(url_for('workers.dashboard'))
    except:
        return redirect(url_for('workers.editProfile'))


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

    # creating the worker att
    att1 = user['role'] + '+' + user['public_id']
    att2 = user['role'] + '-' + user['public_id']

    # Getting the ciphertext from DB
    mp = Patient.get_mp(id)
    vi = Patient.get_vi(id)
    dt = Patient.get_dt(id)
    vip = None
    mpp = None
    dtp = None
    # extracting the policy from the ciphertext
    if mp:
        mp = mp['record']
        _mp = gc.decode(mp)['policy']
        mpp = gc.validate(_mp, att1, att2)
    if vi:
        vi = vi['record']
        _vi = gc.decode(mp)['policy']
        vip = gc.validate(_vi, att1, att2)
    if dt:
        dt = dt['record']
        _dt = gc.decode(mp)['policy']
        dtp = gc.validate(_dt, att1, att2)

    return render_template('patients2/select-record-w.html', user=user, patient=patient, mpp=mpp, vip=vip, dtp=dtp)


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
            records = gc.decode(records)['record']
    elif data == 'vi':
        view = 'Vitals'
        records = Patient.get_vi(id)
        if records:
            records = Patient.get_vi(id)['record']
            records = gc.decode(records)['record']
    elif data == 'dt':
        view = 'Recommended Diagnostic Tests'
        records = Patient.get_dt(id)
        if records:
            records = Patient.get_dt(id)['record']
            records = gc.decode(records)['record']

    return render_template('patients2/data-table-w.html', user=user, patient=patient, view=view, data=data, records=records, json=json, gc=gc)
