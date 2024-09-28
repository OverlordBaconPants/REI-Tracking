# config.py

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'users.json')
    OTHER_DATA_FILE = os.path.join('data', 'data.json')