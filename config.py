# config.py

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'svg', 'pdf', 'jpg'}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB limit

    # JSON file paths
    USERS_FILE = os.path.join(DATA_DIR, 'users.json')
    PROPERTIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'properties.json')
    TRANSACTIONS_FILE = os.path.join(DATA_DIR, 'transactions.json')
    CATEGORIES_FILE = os.path.join(DATA_DIR, 'categories.json')
    REIMBURSEMENTS_FILE = os.path.join(DATA_DIR, 'reimbursements.json')

    GEOAPIFY_API_KEY = 'f9577704874047cd8fc962b020db0d20'