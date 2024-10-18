import pytest
from app import create_app

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_app_creation(app):
    """Test that the app is created successfully."""
    assert app is not None
    assert app.config['TESTING'] == True

def test_hello_world(client):
    """Test the hello world route, if it exists."""
    response = client.get('/')
    assert response.status_code == 200
    # Uncomment and adjust the following line if you have a specific response
    # assert b"Hello, World!" in response.data

# Add more tests as needed