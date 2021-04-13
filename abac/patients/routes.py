from flask import Blueprint, render_template, request, url_for, redirect, flash, session, current_app, jsonify
from abac.patients.models import Patient
from abac.admin.models import Admin
from abac.workers.models import Worker
from abac.patients.utils import login_required, already_logged_in
from rsb import generateCipher
import json
import textwrap

# attaching the patients blueprint
patients = Blueprint('patients', __name__)


# the signup route
@patients.get('/signup/')
@already_logged_in
def register():
    url = '/patients/signup/'
    return render_template('patients/register.html', url=url)


# the signup post route
@patients.post('/signup/')
@already_logged_in
def signup():
    url = '/patients/signup/'
    # collecting form data
    form = request.form
    name = form['name']
    email = form['email']
    password = form['password']
    re_password = form['re_password']
    address = form['address']
    number = form['number']
    gender = form['gender']
    errors = {}
    # handling form validation
    if password != re_password:
        errors['password'] = 'Passwords do not match'
    if Patient.check_email(email):
        errors['email'] = 'That email is already in use'
    if Patient.check_number(number):
        errors['number'] = 'That phone number is already in use'
    if len(errors) > 0:
        return render_template('patients/register.html', url=url, errors=errors)
    patient = Patient(name, email, password, address, number, gender)
    patient.signup()
    data = {
        "eventName": f"{form['name']} Registered as a New Patient"
    }
    Admin.recent(data)

    return redirect(url_for('patients.login'))


# the signin route
@patients.get('/signin/')
@already_logged_in
def signin():
    url = '/patients/signin/'
    return render_template('patients/login.html', url=url)


# the signin post route
@patients.post('/signin/')
@already_logged_in
def login():
    # handling form validation
    form = request.form
    data = {
        "identifier": form['email'],
        "password": form["password"]
    }
    user = Patient().signin(data)

    if user == False:

        flash('Invalid Signin Details', "danger")
        return redirect(url_for('patients.signin'))
    else:
        username = user['name'].split(' ')[0]
        # flash(f'Welcome back {username}', "success")
        return redirect(url_for('patients.dashboard'))


# the signout route
@patients.get('/signout/')
@login_required
def logout(user):
    response = Patient.signout()
    if response:
        return redirect(url_for('main.home'))


# the patient dashboard route
@patients.get('/dashboard/')
@login_required
def dashboard(user):

    # instantiating the encryption algorithm
    key = current_app.config['SECRET_KEY'].encode()
    gc = generateCipher(key)

    mp = Patient.get_mp(user['public_id'])
    vi = Patient.get_vi(user['public_id'])
    dt = Patient.get_dt(user['public_id'])
    if mp:
        mp = mp['record']
        mp = gc.decode(mp)['record']
    if vi:
        vi = vi['record']
        vi = gc.decode(vi)['record']
    if dt:
        dt = dt['record']
        dt = gc.decode(dt)['record']

    # getting notifications
    unreads = Patient.get_unread(user['public_id'])

    return render_template('patients2/dashboard-3.html', unreads=unreads, user=user, mp=mp, vi=vi, dt=dt, list=list, dict=dict, json=json, textwrap=textwrap)


# the patient profile route
@patients.get('/profile/')
@login_required
def profile(user):
    # getting notifications
    unreads = Patient.get_unread(user['public_id'])
    return render_template('patients2/profile_new.html', user=user, unreads=unreads)


# the patient profile edit route
@patients.get('/edit_profile/')
@login_required
def editProfile(user):
    # getting notifications
    unreads = Patient.get_unread(user['public_id'])
    return render_template('patients2/profile_edit.html', user=user, unreads=unreads)


# the patient profile edit POST route
@patients.post('/edit_profile/')
@login_required
def postEditProfile(user):
    # collecting form data
    form = request.form
    data = {
        "name": form['name'],
        "email": form['email'],
        "address": form['address'],
        "number": form['number'],
        "gender": form['gender'],
        "age": form['age'],
        "height": form['height'],
        'weight': form['weight']
    }

    try:
        user = user['public_id']
        response = Patient().update_profile(user, data)
        return redirect(url_for('patients.dashboard'))
    except:
        return redirect(url_for('patients.editProfile'))


# the patient password update profile
@patients.post('/edit_password/')
@login_required
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
        response = Patient().update_password(user, data)
        data = {
            "eventName": f"Patient {user['name']} Recently Requested a Password Change"
        }
        Admin.recent(data)
        return redirect(url_for('patients.dashboard'))

    except:
        flash('Invalid Password Provided', 'danger')
        return redirect(url_for('patients.editProfile'))


# the patient inbox route
@patients.get('/inbox/')
@login_required
def inbox(user):

    pid = user['public_id']

    url = '/patients/inbox/send/'

    # getting messages
    messages = Patient.get_messages(pid)
    unreads = Patient.get_unread(pid)
    sents = Patient.sent_messages(pid)
    trashed = Patient.trashed_messages(pid)
    # getting the workers
    workers = Admin.get_workers()
    admins = Admin.get()

    return render_template('patients2/app/index.html', sents=sents, trashed=trashed, url=url, user=user, messages=messages, unreads=unreads, workers=workers, admins=admins)


# the patient send message route
@patients.post('/inbox/send/')
@login_required
def sendMessage(user):

    # collecting form data
    form = request.form
    # sending the message
    Patient.sendMessage(form, user)

    return redirect(url_for('patients.inbox'))


# the grant read access route
@patients.get('/grantread/')
@login_required
def grantRead(user):

    # getting the query parameters
    id = request.args.get('id')
    # getting the type of record and patient to be updated
    record = request.args.get('data')

    # getting the worker
    worker = Worker.get_worker(id)

    # setting the new attribute
    att = worker['role'] + '+' + worker['public_id']
    act = 'read'

    new_policy = {
        "att": att,
        "act": act
    }

    # instantiating the encryption algorithm
    key = current_app.config['SECRET_KEY'].encode()
    gc = generateCipher(key)

    pid = user['public_id']

    if record == 'mp':
        mp = Patient.get_mp(pid)
        if mp:
            mp = mp['record']
            _mp = gc.decode(mp)
            if not (new_policy in _mp['policy']):
                _mp['policy'].append(new_policy)
            # turning the EHR into ciphertext
            ciphertext = gc.encode(_mp)
        Patient().save_mp(pid, ciphertext)
        Patient.grantReadAccess(worker, user, record)
    elif record == 'vi':
        vi = Patient.get_vi(pid)
        if vi:
            vi = vi['record']
            _vi = gc.decode(vi)
            if not (new_policy in _vi['policy']):
                _vi['policy'].append(new_policy)
            # turning the EHR into ciphertext
            ciphertext = gc.encode(_vi)
        Patient().save_vi(pid, ciphertext)
        Patient.grantReadAccess(worker, user, record)
    elif record == 'dt':
        dt = Patient.get_dt(pid)
        if dt:
            dt = dt['record']
            _dt = gc.decode(dt)
            if not (new_policy in _dt['policy']):
                _dt['policy'].append(new_policy)
            # turning the EHR into ciphertext
            ciphertext = gc.encode(_dt)
        Patient().save_dt(pid, ciphertext)
        Patient.grantReadAccess(worker, user, record)
    elif record == 'ph':
        ph = Patient.get_ph(pid)
        if ph:
            ph = ph['record']
            _ph = gc.decode(ph)
            if not (new_policy in _ph['policy']):
                _ph['policy'].append(new_policy)
            # turning the EHR into ciphertext
            ciphertext = gc.encode(_ph)
        Patient().save_ph(pid, ciphertext)
        Patient.grantReadAccess(worker, user, record)

    data = {
        "eventName": f"Patient {user['name']} just granted a {worker['role']} access to view their EHR"
    }
    Admin.recent(data)

    return redirect(url_for('patients.inbox'))


# the grant read and write access route
@patients.get('/grantwrite/')
@login_required
def grantWrite(user):

    # getting the query parameters
    id = request.args.get('id')
    # getting the type of record and patient to be updated
    record = request.args.get('data')

    # getting the worker
    worker = Worker.get_worker(id)

    # setting the new attribute
    att = worker['role'] + '+' + worker['public_id']
    act = 'read+write'

    new_policy = {
        "att": att,
        "act": act
    }

    # instantiating the encryption algorithm
    key = current_app.config['SECRET_KEY'].encode()
    gc = generateCipher(key)

    pid = user['public_id']

    if record == 'mp':
        mp = Patient.get_mp(pid)
        if mp:
            mp = mp['record']
            _mp = gc.decode(mp)
            if not (new_policy in _mp['policy']):
                _mp['policy'].append(new_policy)
            # turning the EHR into ciphertext
            ciphertext = gc.encode(_mp)
        Patient().save_mp(pid, ciphertext)
        Patient.grantWriteAccess(worker, user, record)
    elif record == 'vi':
        vi = Patient.get_vi(pid)
        if vi:
            vi = vi['record']
            _vi = gc.decode(vi)
            if not (new_policy in _vi['policy']):
                _vi['policy'].append(new_policy)
            # turning the EHR into ciphertext
            ciphertext = gc.encode(_vi)
        Patient().save_vi(pid, ciphertext)
        Patient.grantWriteAccess(worker, user, record)
    elif record == 'dt':
        dt = Patient.get_dt(pid)
        if dt:
            dt = dt['record']
            _dt = gc.decode(dt)
            if not (new_policy in _dt['policy']):
                _dt['policy'].append(new_policy)
            # turning the EHR into ciphertext
            ciphertext = gc.encode(_dt)
        Patient().save_dt(pid, ciphertext)
        Patient.grantWriteAccess(worker, user, record)
    elif record == 'ph':
        ph = Patient.get_ph(pid)
        if ph:
            ph = ph['record']
            _ph = gc.decode(ph)
            if not (new_policy in _ph['policy']):
                _ph['policy'].append(new_policy)
            # turning the EHR into ciphertext
            ciphertext = gc.encode(_ph)
        Patient().save_ph(pid, ciphertext)
        Patient.grantWriteAccess(worker, user, record)

    data = {
        "eventName": f"Patient {user['name']} just granted a {worker['role']} access to view and Edit their EHR"
    }
    Admin.recent(data)

    return redirect(url_for('patients.inbox'))


# decline access route
@patients.get('/declineAccess/')
@login_required
def declineAccess(user):

    # getting the query parameters
    id = request.args.get('id')
    # getting the type of record and patient to be updated
    record = request.args.get('data')

    # getting the worker
    worker = Worker.get_worker(id)

    Patient.declineAccess(worker, user, record)
    Patient.deleteRequest(user, worker, record)

    data = {
        "eventName": f"Patient {user['name']} just declined a {worker['role']} access to view or Edit their EHR"
    }
    Admin.recent(data)

    return redirect(url_for('patients.inbox'))


# mark as read route
@patients.post('/inbox/markAsRead/')
@login_required
def markAsRead(user):

    # getting the query parameters
    id = request.args.get('id')

    # building the changes
    data = {
        'hasRead': True
    }

    # marking the message as read
    Patient.updateMessage(id, data)

    return jsonify({'status': True, 'message': 'Message has been marked as read'})


# delete message route
@patients.get('/inbox/delete/')
@login_required
def delete(user):

    # getting the query parameters
    id = request.args.get('id')

    # building the changes
    data = {
        'hasDeleted': True
    }

    # marking the message as read
    Patient.updateMessage(id, data)

    return redirect(url_for('patients.inbox'))


# view appointments routes
@patients.get('/view_appointments/')
@login_required
def viewAppointment(user):

    # getting appointments from DB
    events = Patient.bookings(user['public_id'])
    pasts = Patient.pastBookings(user['public_id'])

    # getting notifications
    unreads = Patient.get_unread(user['public_id'])

    return render_template('patients2/app/event.html', unreads=unreads, events=events, pasts=pasts, user=user)


# book appointments routes
@patients.get('/appointments/')
@login_required
def bookAppointment(user):

    url = '/patients/appointments/'
    # getting the workers
    workers = Admin.get_workers()
    # getting notifications
    unreads = Patient.get_unread(user['public_id'])
    return render_template('patients2/app/book.html', url=url, user=user, workers=workers, unreads=unreads)


# book appointments post routes
@patients.post('/appointments/')
@login_required
def bookAppointments(user):

    # collecting apointment data
    form = request.form

    # booking the appointment
    Patient.book(form, user)

    worker = Worker.get_worker(form['worker'])

    data = {
        "eventName": f"Patient {user['name']} just scheduled an appointment with {worker['role']} {worker['fname']} {worker['lname']}"
    }
    Admin.recent(data)

    return redirect(url_for("patients.viewAppointment"))
