from uuid import uuid4
from abac import bcrypt, mongo
from datetime import datetime
from flask import session


# the User class
class Admin:
    # initializing the class
    def __init__(self, fname=None, lname=None, email=None, password=None, address=None, number=None, gender=None, role=None):
        self.fname = fname
        self.lname = lname
        self.email = email
        self.password = password
        self.address = address
        self.number = number
        self.gender = gender
        self.role = role

    # signup helper function
    def register(self):

        try:
            user = {
                'public_id': uuid4().hex,
                'fname': self.fname.capitalize().strip(),
                'lname': self.lname.capitalize().strip(),
                'email': self.email.lower(),
                'password': bcrypt.generate_password_hash(
                    self.password).decode('utf-8'),
                'number': self.number,
                'address': self.address,
                'gender': self.gender,
                'role': self.role,
                'dateCreated': datetime.utcnow()
            }

            mongo.db.workers.insert_one(user)
        except:
            return False

        return True

    # route for registering recent activities
    @staticmethod
    def recent(data):
        data['public_id'] = uuid4().hex
        data['dateCreated'] = datetime.utcnow()
        mongo.db.recents.insert_one(data)
        return True

     # route for registering recent activities
    @staticmethod
    def recents():
        return mongo.db.recents.find()

    # creating a user session
    @staticmethod
    def init_session(user):
        session['admin_authenticated'] = True
        del user['password']
        del user['_id']
        session['admin_user'] = user
        session.permanent = True
        return user

    # signin helper function
    def signin(self, signin_data):
        # querying user from db with username
        user = mongo.db.admin.find_one(
            {"username": signin_data['identifier'].lower()})

        # validating user and password
        if user and bcrypt.check_password_hash(user["password"], signin_data['password']):
            return self.init_session(user)

        else:
            # querying user from db  with email
            user = mongo.db.admin.find_one(
                {"email": signin_data['identifier'].lower()})

            # validating user and password
            if user and bcrypt.check_password_hash(user["password"], signin_data['password']):
                return self.init_session(user)

        return False

    # get admin helper function
    @staticmethod
    def get():
        return mongo.db.admin.find()

    # signout helper function
    @staticmethod
    def signout():
        if session['admin_authenticated'] and session['admin_user']:
            session['admin_authenticated'] = False
            del session['admin_user']
        return True

    # email validator helper function
    @staticmethod
    def check_email(email):
        return mongo.db.workers.find_one({"email": email.lower()})

    # number validator helper function
    @staticmethod
    def check_number(number):
        return mongo.db.workers.find_one({"number": number})

    # user retrieval helper function
    @staticmethod
    def get_user(public_id):
        return mongo.db.workers.find_one({"public_id": public_id})

    # profile update helper function
    def update_profile(self, id, data):
        try:
            updateData = data
            user = self.get_user(id)

            # creating the update and commiting to the DB
            if len(updateData) > 0:
                update = {"$set": updateData}
                filterData = {'public_id': user['public_id']}
                mongo.db.workers.update_one(filterData, update)

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

    # get all workers
    @staticmethod
    def get_workers(role=None):
        if role:
            return mongo.db.workers.find({"role": role})
        return mongo.db.workers.find()

    # helper function for getting all messages
    @staticmethod
    def get_messages(id):
        return mongo.db.messages.find({'receiver': id}).sort('dateSent', -1)

    @staticmethod
    def get_unread(id):
        return mongo.db.messages.find({'receiver': id, 'hasRead': False}).sort('dateSent', -1)

    # helper function for getting all sent messages
    @staticmethod
    def sent_messages(id):
        return mongo.db.messages.find({'senderId': id}).sort('dateSent', -1)

    # helper function for getting all trashed messages
    @staticmethod
    def trashed_messages(id):
        return mongo.db.messages.find({'senderId': id, "hasDeleted": True}).sort('dateSent', -1)

    # helper function for sending message
    @staticmethod
    def sendMessage(form, user):

        # creating the message object
        new_message = {
            "receiver": form['receiver'],
            "senderName": "Admin",
            "senderId": user['public_id'],
            "dateSent": datetime.utcnow(),
            "hasRead": False,
            "message": form['message'],
            "senderEmail": user['email'],
            "title": form['title'],
            "senderRole": 'Hospital',
            "messageType": "message",
            "hasDeleted": False,
            "messageId": uuid4().hex
        }
        # adding the message to the database
        mongo.db.messages.insert(new_message)

     # helper function for updating messages

    # update message helper function
    @staticmethod
    def updateMessage(id, data):
        # adding the update to the db
        mongo.db.messages.update_one({'messageId': id}, {'$set': data})
        return True
