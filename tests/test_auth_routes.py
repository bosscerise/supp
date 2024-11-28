import pytest
from flask import session
from app.models.user import User

def test_login_page(client):
    """Test that login page loads correctly."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Email' in response.data
    assert b'Password' in response.data

def test_register_page(client):
    """Test that registration page loads correctly."""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Register New Account' in response.data
    assert b'Company Information' in response.data
    assert b'Business Identifiers' in response.data

def test_successful_login(client, test_user):
    """Test successful login."""
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'password',
        'remember_me': False
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Successfully logged in!' in response.data

def test_failed_login(client):
    """Test login with invalid credentials."""
    response = client.post('/auth/login', data={
        'email': 'wrong@example.com',
        'password': 'wrongpassword',
        'remember_me': False
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data

def test_logout(client, auth, test_user):
    """Test logout functionality."""
    # First login
    auth.login()
    
    # Then logout
    response = auth.logout()
    assert response.status_code == 302  # Redirect after logout
    
    # Follow redirect
    response = client.get('/auth/logout', follow_redirects=True)
    assert b'Successfully logged out!' in response.data

def test_successful_registration(client, app):
    """Test successful user registration."""
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123',
        'password2': 'password123',
        'company_name': 'New Company',
        'address': '123 New Street',
        'phone': '1234567890',
        'nif': '123456789012345',
        'nis': '123456789012345',
        'rc': '123456789012345',
        'art': '12345'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Registration successful!' in response.data
    
    # Verify user was created in database
    with app.app_context():
        user = User.query.filter_by(email='new@example.com').first()
        assert user is not None
        assert user.username == 'newuser'
        assert user.company_name == 'New Company'

def test_duplicate_registration(client, test_user):
    """Test registration with existing email."""
    response = client.post('/auth/register', data={
        'username': 'anotheruser',
        'email': 'test@example.com',  # Same as test_user
        'password': 'password123',
        'password2': 'password123',
        'company_name': 'Another Company',
        'address': '456 Another Street',
        'phone': '9876543210',
        'nif': '987654321098765',
        'nis': '987654321098765',
        'rc': '987654321098765',
        'art': '98765'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Please use a different email address' in response.data

def test_profile_page(client, auth, test_user):
    """Test profile page access."""
    # Without login - should redirect to login page
    response = client.get('/auth/profile', follow_redirects=True)
    assert b'Please log in to access this page' in response.data
    
    # With login - should show profile
    auth.login()
    response = client.get('/auth/profile')
    assert response.status_code == 200
    assert b'Profile Information' in response.data
    assert bytes(test_user.username, 'utf-8') in response.data
    assert bytes(test_user.email, 'utf-8') in response.data

def test_change_password(client, auth, test_user):
    """Test password change functionality."""
    # Login first
    auth.login()
    
    # Change password
    response = client.post('/auth/change-password', data={
        'current_password': 'password',
        'new_password': 'newpassword123',
        'new_password2': 'newpassword123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Your password has been updated' in response.data
    
    # Try logging in with new password
    auth.logout()
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'newpassword123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Successfully logged in!' in response.data
