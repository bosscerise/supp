import pytest
from app.forms.auth import LoginForm, RegistrationForm
from app.models.user import User

@pytest.mark.usefixtures('app')
class TestAuthForms:
    def test_valid_login_form(self, app):
        """Test login form with valid data."""
        with app.test_request_context():
            form = LoginForm(
                email='test@example.com',
                password='password123',
                remember_me=True
            )
            assert form.validate() is True

    def test_invalid_login_form(self, app):
        """Test login form with invalid data."""
        with app.test_request_context():
            # Empty form
            form = LoginForm(email='', password='')
            assert form.validate() is False
            assert 'Email is required' in form.email.errors
            assert 'Password is required' in form.password.errors
            
            # Invalid email format
            form = LoginForm(email='invalid-email', password='password123')
            assert form.validate() is False
            assert 'Please enter a valid email address' in form.email.errors

    def test_valid_registration_form(self, app):
        """Test registration form with valid data."""
        with app.test_request_context():
            form = RegistrationForm(
                username='testuser',
                email='test@example.com',
                password='password123',
                password2='password123',
                company_name='Test Company',
                address='123 Test Street',
                phone='0123456789',
                nif='123456789012345',
                nis='123456789012345',
                rc='123456789012345',
                art='12345'
            )
            assert form.validate() is True

    def test_invalid_registration_form(self, app):
        """Test registration form with invalid data."""
        with app.test_request_context():
            # Empty form
            form = RegistrationForm()
            assert form.validate() is False
            assert 'Username is required' in form.username.errors
            assert 'Email is required' in form.email.errors
            assert 'Password is required' in form.password.errors

            # Invalid email format
            form = RegistrationForm(
                username='testuser',
                email='invalid-email',
                password='password123',
                password2='password123',
                company_name='Test Company',
                address='123 Test Street',
                phone='0123456789',
                nif='123456789012345',
                nis='123456789012345',
                rc='123456789012345',
                art='12345'
            )
            assert form.validate() is False
            assert 'Please enter a valid email address' in form.email.errors

            # Password mismatch
            form = RegistrationForm(
                username='testuser',
                email='test@example.com',
                password='password123',
                password2='differentpassword',
                company_name='Test Company',
                address='123 Test Street',
                phone='0123456789',
                nif='123456789012345',
                nis='123456789012345',
                rc='123456789012345',
                art='12345'
            )
            assert form.validate() is False
            assert 'Passwords must match' in form.password2.errors

            # Invalid NIF length
            form = RegistrationForm(
                username='testuser',
                email='test@example.com',
                password='password123',
                password2='password123',
                company_name='Test Company',
                address='123 Test Street',
                phone='0123456789',
                nif='12345',  # Too short
                nis='123456789012345',
                rc='123456789012345',
                art='12345'
            )
            assert form.validate() is False
            assert 'NIF must be between 15 and 20 characters' in form.nif.errors

    def test_unique_email_validation(self, app):
        """Test that registration form validates email uniqueness."""
        with app.test_request_context():
            # Create a user with a specific email
            with app.app_context():
                user = User(
                    username='existinguser',
                    email='existing@example.com',
                    company_name='Existing Company',
                    address='456 Existing Street',
                    phone='9876543210',
                    nif='987654321098765',
                    nis='987654321098765',
                    rc='987654321098765',
                    art='98765'
                )
                user.set_password('password123')
                app.db.session.add(user)
                app.db.session.commit()

            # Try to register with the same email
            form = RegistrationForm(
                username='newuser',
                email='existing@example.com',  # Same email as existing user
                password='password123',
                password2='password123',
                company_name='New Company',
                address='789 New Street',
                phone='1234567890',
                nif='123456789012345',
                nis='123456789012345',
                rc='123456789012345',
                art='12345'
            )
            assert form.validate() is False
            assert 'Email already registered' in form.email.errors
