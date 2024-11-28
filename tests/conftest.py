import os
import tempfile
import pytest
from app import create_app, db
from app.models.user import User

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False  # Disable CSRF tokens in tests
    })

    # Create the database and load test data
    with app.app_context():
        db.create_all()
        yield app

    # Cleanup after test is complete
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def auth(client):
    """Authentication helper class for tests."""
    class AuthActions:
        def __init__(self, client):
            self._client = client

        def login(self, email='test@example.com', password='password'):
            return self._client.post(
                '/auth/login',
                data={'email': email, 'password': password}
            )

        def logout(self):
            return self._client.get('/auth/logout')

    return AuthActions(client)

@pytest.fixture
def test_user(app):
    """Create a test user."""
    user = User(
        username='testuser',
        email='test@example.com',
        company_name='Test Company',
        address='123 Test Street',
        phone='1234567890',
        nif='123456789012345',
        nis='123456789012345',
        rc='123456789012345',
        art='12345',
        is_active=True
    )
    user.set_password('password')
    
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        
    return user
