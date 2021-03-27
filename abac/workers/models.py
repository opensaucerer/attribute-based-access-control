from uuid import uuid4
from abac import bcrypt, mongo
from datetime import datetime
from flask import session


# the User class
class Worker:
    # initializing the class
    def __init__(self):
        pass

    # signin helper function
    def signin(self, signin_data):
        # querying user from db with username
        user = mongo.db.workers.find_one(
            {"username": signin_data['identifier'].lower()})

        # validating user and password
        if user and bcrypt.check_password_hash(user["password"], signin_data['password']):
            return self.init_session(user)

        else:
            # querying user from db  with email
            user = mongo.db.workers.find_one(
                {"email": signin_data['identifier'].lower()})

            # validating user and password
            if user and bcrypt.check_password_hash(user["password"], signin_data['password']):
                return self.init_session(user)

        return False

    # creating a user session
    @staticmethod
    def init_session(user):
        session['worker_authenticated'] = True
        del user['password']
        del user['_id']
        session['worker_user'] = user
        session.permanent = True
        return user

    # signout helper function
    @staticmethod
    def signout():
        if session['worker_authenticated'] and session['worker_user']:
            session['worker_authenticated'] = False
            del session['worker_user']
        return True

    @staticmethod
    def get_worker(id):
        return mongo.db.workers.find_one({'public_id': id})

    # profile update helper function
    def update_profile(self, id, data):
        try:
            updateData = data
            user = self.get_worker(id)

            # creating the update and commiting to the DB
            if len(updateData) > 0:
                update = {"$set": updateData}
                filterData = {'public_id': user['public_id']}
                mongo.db.workers.update_one(filterData, update)

            # getting the new data of the user
            userUpdate = self.get_worker(id)
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
