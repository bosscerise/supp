from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    """
    User Model for storing supplier information and authentication details.
    
    This model represents a supplier in the system and stores all necessary
    business information required for Algerian commerce documentation.
    
    Attributes:
        id (int): Primary key
        username (str): Unique username for authentication
        email (str): Unique email address
        password_hash (str): Hashed password for security
        company_name (str): Official registered company name
        address (str): Complete business address
        phone (str): Contact phone number
        nif (str): Numéro d'Identification Fiscale (Tax ID)
        nis (str): Numéro d'Identification Statistique (Statistical ID)
        rc (str): Registre de Commerce (Commercial Registry)
        art (str): Article d'Imposition (Tax Article Number)
        created_at (datetime): Account creation timestamp
        is_active (bool): Account status
        last_login (datetime): Last login timestamp
    
    Relationships:
        products: One-to-Many relationship with Product model
        clients: One-to-Many relationship with Client model
        invoices: One-to-Many relationship with Invoice model
        transactions: One-to-Many relationship with Transaction model
    """
    
    __tablename__ = 'users'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Authentication Fields
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    
    # Business Information
    company_name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    
    # Algerian Business Identifiers
    nif = db.Column(db.String(20), unique=True, nullable=False)  # Numéro d'Identification Fiscale
    nis = db.Column(db.String(20), unique=True, nullable=False)  # Numéro d'Identification Statistique
    rc = db.Column(db.String(20), unique=True, nullable=False)   # Registre de Commerce
    art = db.Column(db.String(20), nullable=False)               # Article d'Imposition
    
    # Timestamps and Status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against stored hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    @property
    def total_sales(self):
        """Calculate total sales amount for all paid invoices"""
        return sum(invoice.total_ttc for invoice in self.invoices if invoice.status == 'paid')
    
    @property
    def pending_payments(self):
        """Calculate total pending payments from all unpaid invoices"""
        return sum(invoice.total_ttc for invoice in self.invoices if invoice.status == 'pending')

@login_manager.user_loader
def load_user(id):
    """Flask-Login user loader function"""
    return User.query.get(int(id))
