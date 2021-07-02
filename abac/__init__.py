from flask import Flask
from abac.config import Config
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_pymongo import PyMongo


# instantiating  pymongo
mongo = PyMongo()
# mongo = "make"

# instantiating bcrypt for password hash
bcrypt = Bcrypt()

# setting up CORS
cors = CORS()


# creating the app function
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    mongo.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)

    from abac.main.routes import main, page_not_found
    from abac.patients.routes import patients
    from abac.admin.routes import admin
    app.register_error_handler(404, page_not_found)
    app.register_blueprint(main)
    app.register_blueprint(patients, url_prefix='/patients')
    app.register_blueprint(admin, url_prefix='/admin')

    return app
