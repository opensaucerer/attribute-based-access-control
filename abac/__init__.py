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

    from abac.main.routes import main
    from abac.patients.routes import patients
    app.register_blueprint(main)
    app.register_blueprint(patients, url_prefix='/patients')

    return app
