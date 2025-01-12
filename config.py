# config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration with common settings"""
    # Load secret key from environment variable with no default
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set in environment variables")
    
    # Base directory defaults to current directory for development
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # File upload settings
    ALLOWED_EXTENSIONS = {'png', 'svg', 'pdf', 'jpg', 'jpeg', 'csv', 'xls', 'xlsx'}
    ALLOWED_DOCUMENTATION_EXTENSIONS = {'png', 'svg', 'pdf', 'jpg'}
    ALLOWED_IMPORT_EXTENSIONS = {'csv', 'xls', 'xlsx'}
    
    # Load max content length from environment variable
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 5 * 1024 * 1024))  # Default 5MB
    
    # Load API key from environment variable with no default
    GEOAPIFY_API_KEY = os.environ.get('GEOAPIFY_API_KEY')
    if not GEOAPIFY_API_KEY:
        raise ValueError("No GEOAPIFY_API_KEY set in environment variables")
    
    def __init__(self):
        # Directory structure
        self.DATA_DIR = os.path.join(self.BASE_DIR, 'data')
        self.ANALYSES_DIR = os.path.join(self.DATA_DIR, 'analyses')
        self.UPLOAD_FOLDER = os.path.join(self.DATA_DIR, 'uploads')
        self.REIMBURSEMENTS_DIR = os.path.join(self.UPLOAD_FOLDER, 'reimbursements')
        
        # JSON file paths
        self.USERS_FILE = os.path.join(self.DATA_DIR, 'users.json')
        self.PROPERTIES_FILE = os.path.join(self.DATA_DIR, 'properties.json')
        self.TRANSACTIONS_FILE = os.path.join(self.DATA_DIR, 'transactions.json')
        self.CATEGORIES_FILE = os.path.join(self.DATA_DIR, 'categories.json')
        
        # Create necessary directories if not in production
        if not os.environ.get('RENDER'):
            self.create_directories()

    def create_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(self.DATA_DIR, exist_ok=True)
        os.makedirs(self.ANALYSES_DIR, exist_ok=True)
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(self.REIMBURSEMENTS_DIR, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    def __init__(self):
        super().__init__()
        print(f"Running in development mode. Using BASE_DIR: {self.BASE_DIR}")

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    def __init__(self):
        # For Render.com, use the correct mounted volume path
        self.BASE_DIR = '/opt/render/project/src'
        self.DATA_DIR = '/opt/render/project/src/data'
        self.ANALYSES_DIR = '/opt/render/project/src/data/analyses'
        self.UPLOAD_FOLDER = '/opt/render/project/src/data/uploads'
        self.REIMBURSEMENTS_DIR = os.path.join(self.UPLOAD_FOLDER, 'reimbursements')
        
        # JSON file paths
        self.USERS_FILE = os.path.join(self.DATA_DIR, 'users.json')
        self.PROPERTIES_FILE = os.path.join(self.DATA_DIR, 'properties.json')
        self.TRANSACTIONS_FILE = os.path.join(self.DATA_DIR, 'transactions.json')
        self.CATEGORIES_FILE = os.path.join(self.DATA_DIR, 'categories.json')
        
        print(f"Running in production mode on Render.com")

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    
    def __init__(self):
        self.BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data')
        super().__init__()

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get the current configuration based on environment"""
    if os.environ.get('RENDER'):
        return ProductionConfig()
    
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])()