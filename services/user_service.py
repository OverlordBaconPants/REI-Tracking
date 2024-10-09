# /services/user_services.py


import json
import logging
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_users():
    try:
        with open(current_app.config['USERS_FILE'], 'r') as f:
            users = json.load(f)
            logger.debug(f"Loaded users: {list(users.keys())}")
            return users
    except FileNotFoundError:
        logger.error(f"Users file not found: {current_app.config['USERS_FILE']}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in users file: {current_app.config['USERS_FILE']}")
        return {}

def save_users(users):
    with open(current_app.config['USERS_FILE'], 'w') as f:
        json.dump(users, f, indent=2)
    logger.debug(f"Saved users: {list(users.keys())}")

def get_user_by_email(email):
    users = load_users()
    user = users.get(email)
    if user:
        logger.debug(f"User found: {email}")
        return user
    logger.debug(f"User not found: {email}")
    return None

def create_user(email, name, password, role='User'):
    users = load_users()
    if email not in users:
        hashed_password = hash_password(password)
        users[email] = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'role': role
        }
        save_users(users)
        logger.info(f"New user created: {email}")
        return True
    logger.warning(f"Attempt to create existing user: {email}")
    return False

def hash_password(password):
    return generate_password_hash(password, method='pbkdf2:sha256')

def verify_password(stored_password, provided_password):
    result = check_password_hash(stored_password, provided_password)
    logger.debug(f"Password verification result: {result}")
    return result

def update_user_password(email, new_password):
    users = load_users()
    if email in users:
        hashed_password = hash_password(new_password)
        users[email]['password'] = hashed_password
        save_users(users)
        logger.info(f"Password updated for user: {email}")
        return True
    logger.warning(f"Attempt to update password for non-existent user: {email}")
    return False