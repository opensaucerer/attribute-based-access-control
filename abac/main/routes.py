from flask import Blueprint, render_template, request, url_for, redirect

# attaching the main blueprint
main = Blueprint('main', __name__)


# the home route
@main.get('/')
@main.get('/home/')
@main.get('/index/')
def home():
    return render_template('main/index.html')


# the about page
@main.get('/about/')
def about():
    return render_template('main/about.html')
