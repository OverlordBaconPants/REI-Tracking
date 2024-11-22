# models.py
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, name, password, role):
        self.id = id
        self.email = email
        self.name = name
        self.password = password
        self.role = role

    def get_id(self):
        return self.email

    @staticmethod
    def get(user_id):
        from services.user_service import load_users
        users = load_users()
        user_data = users.get(user_id)
        if user_data:
            return User(
                id=user_data['email'],
                email=user_data['email'],
                name=user_data['name'],
                password=user_data['password'],
                role=user_data.get('role', 'User')
        )
        return None

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False
    
    @property
    def is_admin(self):
        return self.role.lower() == 'admin'