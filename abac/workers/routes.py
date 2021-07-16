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
    # getting notifications
    unreads = Worker.get_unread(user['public_id'])

    return render_template('patients2/dashboard-w.html', unreads=unreads, user=user, data=data, patients=patients)


# the patient profile edit route
@workers.get('/edit_profile/')
@worker_login_required
def editProfile(user):
    url = '/workers/edit_profile/'
    # getting notifications
    unreads = Worker.get_unread(user['public_id'])
    return render_template('patients2/worker_edit.html', unreads=unreads, user=user, worker=user)


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


# the worker password update route
@workers.post('/edit_password/')
@worker_login_required
def editPassword(user):

    # collecting form data
    form = request.form
    data = {
        "cpass": form['cpass'],
        "npass": form['npass'],
    }
    # updating the user password
    try:
        user = user['public_id']
        response = Worker().update_password(user, data)
        return redirect(url_for('workers.dashboard'))

    except:
        flash('Invalid Password Provided', 'danger')
        return redirect(url_for('workers.editProfile'))


# the patient public profile
@workers.get('/patients/profile/')
@worker_login_required
def patientProfile(user):
    # getting the patient id
    id = request.args.get('id')
    patient = Patient.get_user(id)
    # getting notifications
    unreads = Worker.get_unread(user['public_id'])
    return render_template('patients2/profile_new_2.html', unreads=unreads, patient=patient, user=user)


# the list patients route
@workers.get('/patients/list/')
@worker_login_required
def listPatients(user):
    patients = Patient.get_patients()

    # getting notifications
    unreads = Worker.get_unread(user['public_id'])

    return render_template('patients2/patient-list-w.html', unreads=unreads, user=user, patients=patients)


# the retrieve record categories route
@workers.get('/patients/records/')
@worker_login_required
def getRecord(user):
    # getting the query parameters
    id = request.args.get('id')
    # getting the patient
    patient = Patient.get_user(id)

    # checking if request has already been sent
    sent = Worker.checkRequest(id, user['public_id'])

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
    ph = Patient.get_ph(id)
    vip = True
    mpp = True
    dtp = True
    # extracting the policy from the ciphertext
    if mp:
        mp = mp['record']
        _mp = gc.decode(mp)['policy']
        mpp = gc.validate(_mp, att1, att2)
    if vi:
        vi = vi['record']
        _vi = gc.decode(vi)['policy']
        vip = gc.validate(_vi, att1, att2)
    if dt:
        dt = dt['record']
        _dt = gc.decode(dt)['policy']
        dtp = gc.validate(_dt, att1, att2)
    # if ph:
    #     ph = ph['record']
    #     _ph = gc.decode(ph)['policy']
    #     dtp = gc.validate(_ph, att1, att2)

    # getting notifications
    unreads = Worker.get_unread(user['public_id'])

    return render_template('patients2/select-record-w.html', unreads=unreads, user=user, patient=patient, mpp=mpp, vip=vip, dtp=dtp, sent=sent)


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
    elif data == 'ph':
        view = 'Personal and Health History'
        records = Patient.get_ph(id)
        if records:
            records = Patient.get_ph(id)['record']
            records = gc.decode(records)['record']

    # getting notifications
    unreads = Worker.get_unread(user['public_id'])

    return render_template('patients2/data-table-w.html', unreads=unreads, user=user, patient=patient, view=view, data=data, records=records, json=json, gc=gc)


# the view records route
@workers.get('/request/')
@worker_login_required
def requestAccess(user):
    # getting the query parameters
    id = request.args.get('id')
    data = request.args.get('data')
    # getting the patient
    patient = Patient.get_user(id)

    Worker.requestAccess(patient, user, data)
    Worker.saveRequest(patient, user, data)

    return redirect(url_for('workers.getRecord', id=id, data=data))


# the edit records route
@workers.get('/patients/edit/')
@worker_login_required
def editRecord(user):
    # getting the query parameters
    id = request.args.get('id')
    data = request.args.get('data')
    # getting the patient
    patient = Patient.get_user(id)
    # getting the workers
    workers = Admin.get_workers()

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
    elif data == 'ph':
        view = 'Personal and Health History'
        records = Patient.get_ph(id)
        if records:
            records = Patient.get_ph(id)['record']
            records = gc.decode(records)['record']

    # getting notifications
    unreads = Worker.get_unread(user['public_id'])

    return render_template('patients2/table-editable-w.html', unreads=unreads, user=user, workers=workers, patient=patient, view=view, data=data, records=records, json=json, len=len)


# the edit records route
@workers.post('/patients/records/save/')
@worker_login_required
def saveRecord(user):
    # getting the request data
    data = request.get_json()

    # instantiating the encryption algorithm
    key = current_app.config['SECRET_KEY'].encode()
    gc = generateCipher(key)

    # getting the type of record and patient to be updated
    record = request.args.get('record')
    pid = request.args.get('id')

    if record == 'mp':
        mp = Patient.get_mp(pid)
        if mp:
            mp = mp['record']
            _mp = gc.decode(mp)['policy']
            data['policy'] = _mp
            # turning the EHR into ciphertext
            ciphertext = gc.encode(data)
        Patient().save_mp(pid, ciphertext)
    elif record == 'vi':
        vi = Patient.get_vi(pid)
        if vi:
            vi = vi['record']
            _vi = gc.decode(vi)['policy']
            data['policy'] = _vi
            # turning the EHR into ciphertext
            ciphertext = gc.encode(data)
        Patient().save_vi(pid, ciphertext)
    elif record == 'dt':
        dt = Patient.get_dt(pid)
        if dt:
            dt = dt['record']
            _dt = gc.decode(dt)['policy']
            data['policy'] = _dt
            # turning the EHR into ciphertext
            ciphertext = gc.encode(data)
        Patient().save_dt(pid, ciphertext)
    elif record == 'ph':
        ph = Patient.get_ph(pid)
        if ph:
            ph = ph['record']
            _ph = gc.decode(ph)['policy']
            data['policy'] = _ph
            # turning the EHR into ciphertext
            ciphertext = gc.encode(data)
        Patient().save_ph(pid, ciphertext)

    return jsonify({"status": True, "message": "EHR Update Successfully"})


# the worker inbox route
@workers.get('/inbox/')
@worker_login_required
def inbox(user):

    pid = user['public_id']

    url = '/workers/inbox/send/'

    # getting messages
    messages = Worker.get_messages(pid)
    unreads = Worker.get_unread(pid)
    sents = Worker.sent_messages(pid)
    trashed = Worker.trashed_messages(pid)
    # getting the workers
    patients = Patient.get_patients()
    admins = Admin.get()
    workers = Admin.get_workers()

    return render_template('patients2/app/index-w.html', url=url, workers=workers, user=user, messages=messages, unreads=unreads, patients=patients, admins=admins, sents=sents, trashed=trashed)


# the worker send message route
@workers.post('/inbox/send/')
@worker_login_required
def sendMessage(user):

    # collecting form data
    form = request.form
    # sending the message
    Worker.sendMessage(form, user)

    return redirect(url_for('workers.inbox'))


# mark as read route
@workers.post('/inbox/markAsRead/')
@worker_login_required
def markAsRead(user):

    # getting the query parameters
    id = request.args.get('id')

    # building the changes
    data = {
        'hasRead': True
    }

    print('GOT HERE')

    # marking the message as read
    Worker.updateMessage(id, data)

    print('GOT HERE')

    return jsonify({'status': True, 'message': 'Message has been marked as read'})


# delete message route
@workers.get('/inbox/delete/')
@worker_login_required
def delete(user):

    # getting the query parameters
    id = request.args.get('id')

    # building the changes
    data = {
        'hasDeleted': True
    }

    # marking the message as read
    Worker.updateMessage(id, data)

    return redirect(url_for('workers.inbox'))


# view appointments routes
@workers.get('/view_appointments/')
@worker_login_required
def viewAppointment(user):

    # getting appointments from DB
    events = Worker.bookings(user['public_id'])
    pasts = Worker.pastBookings(user['public_id'])

    # getting notifications
    unreads = Worker.get_unread(user['public_id'])

    return render_template('patients2/app/event-w.html', events=events, unreads=unreads, pasts=pasts, user=user)


# mark as done appointments routes
@workers.get('/appointments/done/')
@worker_login_required
def completeAppointment(user):

    # getting the event ID
    id = request.args.get('id')

    # marking the appoinment as done
    Worker.bookComplete(id)

    return redirect(url_for('workers.viewAppointment'))


# view requested access routes
@workers.get('/records/requests/')
@worker_login_required
def getRequests(user):
    sents = Worker.getRequests(user['public_id'])
    return render_template('patients2/requests.html', sents=sents)
