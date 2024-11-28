from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    """
    Login form for user authentication.
    
    Fields:
        email: User's email address
        password: User's password
        remember_me: Remember login session
    """
    email = StringField('Email', validators=[
        DataRequired(message="Email is required"),
        Email(message="Please enter a valid email address")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required")
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    """
    Registration form for new supplier accounts.
    
    Fields:
        username: Unique username
        email: Unique email address
        password: Account password
        password2: Password confirmation
        company_name: Official company name
        address: Business address
        phone: Contact phone number
        nif: Numéro d'Identification Fiscale
        nis: Numéro d'Identification Statistique
        rc: Registre de Commerce
        art: Article d'Imposition
    """
    username = StringField('Username', validators=[
        DataRequired(message="Username is required"),
        Length(min=4, max=64, message="Username must be between 4 and 64 characters")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Email is required"),
        Email(message="Please enter a valid email address"),
        Length(max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required"),
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(message="Please confirm your password"),
        EqualTo('password', message="Passwords must match")
    ])
    
    # Company Information
    company_name = StringField('Company Name', validators=[
        DataRequired(message="Company name is required"),
        Length(max=120)
    ])
    address = StringField('Business Address', validators=[
        DataRequired(message="Business address is required"),
        Length(max=200)
    ])
    phone = StringField('Phone Number', validators=[
        DataRequired(message="Phone number is required"),
        Length(max=20)
    ])
    
    # Algerian Business Identifiers
    nif = StringField('NIF (Numéro d\'Identification Fiscale)', validators=[
        DataRequired(message="NIF is required"),
        Length(min=15, max=20, message="NIF must be between 15 and 20 characters")
    ])
    nis = StringField('NIS (Numéro d\'Identification Statistique)', validators=[
        DataRequired(message="NIS is required"),
        Length(min=15, max=20, message="NIS must be between 15 and 20 characters")
    ])
    rc = StringField('RC (Registre de Commerce)', validators=[
        DataRequired(message="RC is required"),
        Length(min=15, max=20, message="RC must be between 15 and 20 characters")
    ])
    art = StringField('Article d\'Imposition', validators=[
        DataRequired(message="Article d'Imposition is required"),
        Length(max=20)
    ])
    
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Validate username uniqueness"""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        """Validate email uniqueness"""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
    
    def validate_nif(self, nif):
        """Validate NIF uniqueness and format"""
        user = User.query.filter_by(nif=nif.data).first()
        if user is not None:
            raise ValidationError('This NIF is already registered.')
        # Add additional NIF format validation if needed
    
    def validate_nis(self, nis):
        """Validate NIS uniqueness and format"""
        user = User.query.filter_by(nis=nis.data).first()
        if user is not None:
            raise ValidationError('This NIS is already registered.')
        # Add additional NIS format validation if needed
    
    def validate_rc(self, rc):
        """Validate RC uniqueness and format"""
        user = User.query.filter_by(rc=rc.data).first()
        if user is not None:
            raise ValidationError('This RC is already registered.')
        # Add additional RC format validation if needed
