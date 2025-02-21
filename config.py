import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import tempfile

# Load environment variables from .env file
load_dotenv()

def setup_logging(config_name):
    """Configure logging based on the configuration"""
    # Use temp directory for log files in development
    if config_name == 'development':
        log_dir = os.path.join(tempfile.gettempdir(), 'transactions_app_logs')
    else:
        # In production, use the app's data directory
        log_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'logs')
    
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'transactions.log')
    
    # Create handlers
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5
    )
    console_handler = logging.StreamHandler()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if config_name == 'development' else logging.INFO)
    
    # Silence watchdog logs
    logging.getLogger('watchdog').setLevel(logging.WARNING)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers = []
    
    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger

class Config:
    """Base configuration with common settings"""
    # Load secret key from environment variable with no default
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set in environment variables")
    
    # Base directory defaults to current directory for development
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # File upload settings with documentation
    ALLOWED_EXTENSIONS = {'png', 'svg', 'pdf', 'jpg', 'jpeg', 'csv', 'xls', 'xlsx'}
    ALLOWED_DOCUMENTATION_EXTENSIONS = {'png', 'svg', 'pdf', 'jpg', 'jpeg'}
    ALLOWED_IMPORT_EXTENSIONS = {'csv', 'xls', 'xlsx'}
    
    # Load max content length from environment variable
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 8 * 1024 * 1024))  # Default 8MB
    
    # Load API key from environment variable with no default
    GEOAPIFY_API_KEY = os.environ.get('GEOAPIFY_API_KEY')
    if not GEOAPIFY_API_KEY:
        raise ValueError("No GEOAPIFY_API_KEY set in environment variables")

    def __init__(self):
        # Directory structure - simplified to one uploads directory
        self.DATA_DIR = os.path.join(self.BASE_DIR, 'data')
        self.ANALYSES_DIR = os.path.join(self.DATA_DIR, 'analyses')
        self.UPLOAD_FOLDER = os.path.join(self.DATA_DIR, 'uploads')  # Single uploads directory
        
        # JSON file paths
        self.USERS_FILE = os.path.join(self.DATA_DIR, 'users.json')
        self.PROPERTIES_FILE = os.path.join(self.DATA_DIR, 'properties.json')
        self.TRANSACTIONS_FILE = os.path.join(self.DATA_DIR, 'transactions.json')
        self.CATEGORIES_FILE = os.path.join(self.DATA_DIR, 'categories.json')
        
        # Add comps data directory
        self.COMPS_DIR = os.path.join(self.DATA_DIR, 'comps')

        # RentCast API Configuration
        self.RENTCAST_API_KEY = os.environ.get('RENTCASTCOMPS_KEY')
        if not self.RENTCAST_API_KEY:
            raise ValueError("No RENTCASTCOMPS_KEY set in environment variables")
        
        self.RENTCAST_API_BASE_URL = "https://api.rentcast.io/v1"
        self.RENTCAST_COMP_DEFAULTS = {
            'maxRadius': 1.0,  # 1 mile radius
            'daysOld': 180,    # Last 6 months
            'compCount': 10     # Number of comps to return
        }

        # Session limits for comps
        self.MAX_COMP_RUNS_PER_SESSION = 3

        # Create necessary directories if not in production
        if not os.environ.get('RENDER'):
            self.create_directories()

    def create_directories(self):
        """Create necessary directories if they don't exist"""
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
        # For Render.com, use the correct mounted volume path
        self.BASE_DIR = '/opt/render/project/src'
        self.DATA_DIR = '/opt/render/project/src/data'
        self.ANALYSES_DIR = '/opt/render/project/src/data/analyses'
        self.UPLOAD_FOLDER = '/opt/render/project/src/data/uploads'  # Single uploads directory
        
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