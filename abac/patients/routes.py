from flask import Blueprint, render_template, request, url_for, redirect, flash
from abac.patients.models import Patient
from abac.patients.utils import login_required, already_logged_in

# attaching the patients blueprint
patients = Blueprint('patients', __name__)


# the signup route
@patients.get('/signup/')
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
    address = form['address']
    number = form['number']
    gender = form['gender']
    errors = {}
    # handling form validation
    if Patient.check_email(email):
        errors['email'] = 'That email is already in use'
    if Patient.check_number(number):
        errors['number'] = 'That phone number is already in use'
        return render_template('patients/register.html', url=url, errors=errors)
    patient = Patient(name, email, password, address, number, gender)
    patient.signup()

    return redirect(url_for('patients.login'))


# the signin route
@patients.get('/signin/')
@already_logged_in
def login():
    url = '/patients/signin/'
    return render_template('patients/login.html', url=url)


# the signin post route
@patients.post('/signin/')
def signin():
    # handling form validation
    form = request.form
    data = {
        "identifier": form['email'],
        "password": form["password"]
    }
    user = Patient().signin(data)

    if user == False:
        print('FALSE DATA')
        flash('Invalid Signin Details', "danger")
        return redirect(url_for('patients.signin'))
    else:
        username = user['name'].split(' ')[0]
        flash(f'Welcome back {username}', "success")
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
    return render_template('patients2/dashboard-3.html', user=user)


# the patient profile route
@patients.get('/profile/')
@login_required
def profile(user):
    return render_template('patients2/profile_new.html', user=user)


# the patient profile edit route
@patients.get('/edit_profile/')
@login_required
def editProfile(user):
    return render_template('patients2/profile_edit.html', user=user)


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
        "age": form['age']
    }

    try:
        user = user['public_id']
        response = Patient().update_profile(user, data)
        return redirect(url_for('patients.dashboard'))
    except:
        return redirect(url_for('patients.editProfile'))