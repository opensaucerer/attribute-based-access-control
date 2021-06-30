import os
from dotenv import load_dotenv
load_dotenv()


class Config:

    MONGO_URI = os.environ.get('MONGO_URI')
    SECRET_KEY = os.environ.get('SECRET_KEY')
