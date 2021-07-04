from uuid import uuid4
from abac import bcrypt, mongo
from datetime import datetime
from flask import session
import safe


# the User class
class Patient:
    # initializing the class
    def __init__(self, name=None, email=None, password=None, address=None, number=None, gender=None):
        self.name = name
        self.email = email
        self.password = password
        self.address = address
        self.number = number
        self.gender = gender

    # signup helper function
    def signup(self):

        try:
            user = {
                'public_id': uuid4().hex,
                'name': self.name.title().strip(),
                'email': self.email.lower(),
                'password': bcrypt.generate_password_hash(
                    self.password).decode('utf-8'),
                'number': self.number,
                'address': self.address,
                'gender': self.gender,
                'dateCreated': datetime.utcnow()
            }

            mongo.db.patients.insert_one(user)
        except:
            return False

        return True

    # creating a user session
    @staticmethod
    def init_session(user):
        session['is_authenticated'] = True
        del user['password']
        del user['_id']
        session['current_user'] = user
        session.permanent = True
        return user

    # signin helper function
    def signin(self, signin_data):
        # querying user from db with username
        user = mongo.db.patients.find_one(
            {"username": signin_data['identifier'].lower()})

        # validating user and password
        if user and bcrypt.check_password_hash(user["password"], signin_data['password']):
            return self.init_session(user)

        else:
            # querying user from db  with email
            user = mongo.db.patients.find_one(
                {"email": signin_data['identifier'].lower()})

            # validating user and password
            if user and bcrypt.check_password_hash(user["password"], signin_data['password']):
                return self.init_session(user)

        return False

    # signout helper function
    @staticmethod
    def signout():
        if session['is_authenticated'] and session['current_user']:
            session['is_authenticated'] = False
            del session['current_user']
        return True

    # email validator helper function
    @staticmethod
    def check_email(email):
        return mongo.db.patients.find_one({"email": email.lower()})

    # number validator helper function
    @staticmethod
    def check_number(number):
        return mongo.db.patients.find_one({"number": number})

    # user retrieval helper function
    @staticmethod
    def get_user(public_id):
        return mongo.db.patients.find_one({"public_id": public_id})

    # profile update helper function
    def update_profile(self, id, data):
        try:
            updateData = data
            user = self.get_user(id)

            # creating the update and commiting to the DB
            if len(updateData) > 0:
                update = {"$set": updateData}
                filterData = {'public_id': user['public_id']}
                mongo.db.patients.update_one(filterData, update)

            # getting the new data of the user
            userUpdate = self.get_user(id)
            # starting a new session for the user
            userData = self.init_session(userUpdate)

            response = {
                "status": True,
                "message": "Your profile has been updated successfully",
                "userData": userData
            }

        except:
            response = {
                "status": False,
                "error": "Something went wrong. Please try again."
            }
            # return response
        return response

    # get all patients
    @staticmethod
    def get_patients():
        return mongo.db.patients.find()

    # password update helper function
    def update_password(self, id, data):

        updateData = {}

        user = self.get_user(id)
        # checking the old password
        if not (bcrypt.check_password_hash(user['password'], data['cpass'])):
            raise ValueError

        # hashing the new password
        newPassword = bcrypt.generate_password_hash(
            data['npass']).decode("utf-8")

        # adding password to the db
        mongo.db.patients.update_one(
            {'public_id': id}, {'$set': {'password': newPassword}})

    # helper functions for getting patient records

    @staticmethod
    def get_mp(id):
        # medicine prescription
        return mongo.db.medicine.find({'public_id': id})

    @staticmethod
    def get_vi(id):
        # patient vitals
        return mongo.db.vitals.find({'public_id': id})

    @staticmethod
    def get_dt(id):
        # diagnostics tests
        return mongo.db.tests.find({'public_id': id})
    # helper functions for getting patient records end
