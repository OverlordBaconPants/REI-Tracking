# config.py

import os

class Config:
    """Base configuration with common settings"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # Base directory defaults to current directory for development
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # File upload settings
    ALLOWED_EXTENSIONS = {'png', 'svg', 'pdf', 'jpg', 'csv', 'xls', 'xlsx'}
    ALLOWED_DOCUMENTATION_EXTENSIONS = {'png', 'svg', 'pdf', 'jpg'}
    ALLOWED_IMPORT_EXTENSIONS = {'csv', 'xls', 'xlsx'}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB limit
    
    # API Keys
    GEOAPIFY_API_KEY = os.environ.get('GEOAPIFY_API_KEY') or 'f9577704874047cd8fc962b020db0d20'
    
    def __init__(self):
        # Directory structure
        self.DATA_DIR = os.path.join(self.BASE_DIR, 'data')
        self.ANALYSES_DIR = os.path.join(self.DATA_DIR, 'analyses')
        self.UPLOAD_FOLDER = os.path.join(self.BASE_DIR, 'uploads')
        
        # JSON file paths
        self.USERS_FILE = os.path.join(self.DATA_DIR, 'users.json')
        self.PROPERTIES_FILE = os.path.join(self.DATA_DIR, 'properties.json')
        self.TRANSACTIONS_FILE = os.path.join(self.DATA_DIR, 'transactions.json')
        self.CATEGORIES_FILE = os.path.join(self.DATA_DIR, 'categories.json')
        self.REIMBURSEMENTS_FILE = os.path.join(self.DATA_DIR, 'reimbursements.json')
        
        # Create necessary directories
        os.makedirs(self.DATA_DIR, exist_ok=True)
        os.makedirs(self.ANALYSES_DIR, exist_ok=True)
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)

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
        # Override BASE_DIR for Render.com
        self.BASE_DIR = '/data'
        super().__init__()  # Initialize all paths after setting BASE_DIR
        print(f"Running in production mode. Using BASE_DIR: {self.BASE_DIR}")
        print(f"Data directory: {self.DATA_DIR}")
        print(f"Analyses directory: {self.ANALYSES_DIR}")
        print(f"Upload folder: {self.UPLOAD_FOLDER}")
        print(f"Users file: {self.USERS_FILE}")
        print(f"Properties file: {self.PROPERTIES_FILE}")

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    
    def __init__(self):
        self.BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data')
        super().__init__()  # Initialize with test directory

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
        config_instance = ProductionConfig()
        print(f"Using production configuration with mounted path: {config_instance.BASE_DIR}")
        return config_instance
    
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])()