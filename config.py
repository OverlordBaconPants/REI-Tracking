# config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Core Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
    
    # Directory Configuration
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    ANALYSES_DIR = os.path.join(DATA_DIR, 'analyses')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    
    # File Upload Configuration
    ALLOWED_EXTENSIONS = {'png', 'svg', 'pdf', 'jpg', 'csv', 'xls', 'xlsx'}
    ALLOWED_DOCUMENTATION_EXTENSIONS = {'png', 'svg', 'pdf', 'jpg'}
    ALLOWED_IMPORT_EXTENSIONS = {'csv', 'xls', 'xlsx'}
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 5 * 1024 * 1024))  # Default 5MB
    
    # JSON file paths
    USERS_FILE = os.path.join(DATA_DIR, 'users.json')
    PROPERTIES_FILE = os.path.join(DATA_DIR, 'properties.json')
    TRANSACTIONS_FILE = os.path.join(DATA_DIR, 'transactions.json')
    CATEGORIES_FILE = os.path.join(DATA_DIR, 'categories.json')
    REIMBURSEMENTS_FILE = os.path.join(DATA_DIR, 'reimbursements.json')
    
    # API Configuration
    GEOAPIFY_API_KEY = os.environ.get('GEOAPIFY_API_KEY')
    
    def __init__(self):
        # Create necessary directories
        self._create_directories()
        
        # Validate critical configuration
        self._validate_configuration()
    
    def _create_directories(self):
        """Create necessary directories if they don't exist."""
        os.makedirs(self.DATA_DIR, exist_ok=True)
        os.makedirs(self.ANALYSES_DIR, exist_ok=True)
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
    
    def _validate_configuration(self):
        """Validate critical configuration settings."""
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set")
        
        if not self.GEOAPIFY_API_KEY:
            raise ValueError("GEOAPIFY_API_KEY must be set")
        
        if self.MAX_CONTENT_LENGTH <= 0:
            raise ValueError("MAX_CONTENT_LENGTH must be a positive integer")

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
    def __init__(self):
        super().__init__()
        if self.SECRET_KEY == 'you-will-never-guess':
            raise ValueError("Production SECRET_KEY must be set")

# Dictionary to map environment names to config objects
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Return the appropriate configuration object based on FLASK_ENV."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])