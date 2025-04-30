from __init__ import create_app
from config import setup_logging
import os

# Set up logging based on environment
env = os.environ.get('FLASK_ENV', 'development')
logger = setup_logging(env)

app = create_app()
logger.info(f'Application starting up in {env} mode')

@app.route('/health')
def health_check():
    logger.debug('Health check endpoint accessed')
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True)