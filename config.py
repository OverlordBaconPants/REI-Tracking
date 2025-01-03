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
        self.BASE_DIR = '/opt/render/project/src'                   # Application root
        self.DATA_DIR = '/opt/render/project/src/data'             # Data directory in mounted volume
        self.ANALYSES_DIR = '/opt/render/project/src/data/analyses' # Analyses subdirectory
        self.UPLOAD_FOLDER = '/opt/render/project/src/data/uploads' # Upload directory in mounted volume
        self.REIMBURSEMENTS_DIR = os.path.join(self.UPLOAD_FOLDER, 'reimbursements')
        
        # JSON file paths
        self.USERS_FILE = os.path.join(self.DATA_DIR, 'users.json')
        self.PROPERTIES_FILE = os.path.join(self.DATA_DIR, 'properties.json')
        self.TRANSACTIONS_FILE = os.path.join(self.DATA_DIR, 'transactions.json')
        self.CATEGORIES_FILE = os.path.join(self.DATA_DIR, 'categories.json')
        
        print(f"Running in production mode on Render.com")
        print(f"Base directory: {self.BASE_DIR}")
        print(f"Data directory: {self.DATA_DIR}")
        print(f"Upload folder: {self.UPLOAD_FOLDER}")
        print(f"Reimbursements directory: {self.REIMBURSEMENTS_DIR}")

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