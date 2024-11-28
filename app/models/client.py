from app import db
from datetime import datetime

class Client(db.Model):
    """
    Client Model for storing customer information.
    
    This model represents business clients (B2B) with all necessary
    information required for Algerian business documentation and invoicing.
    
    Attributes:
        id (int): Primary key
        name (str): Client company name
        contact_person (str): Primary contact person name
        address (str): Complete business address
        phone (str): Contact phone number
        email (str): Contact email address
        nif (str): Numéro d'Identification Fiscale (Tax ID)
        nis (str): Numéro d'Identification Statistique (Statistical ID)
        rc (str): Registre de Commerce (Commercial Registry)
        art (str): Article d'Imposition (Tax Article Number)
        payment_terms (int): Payment terms in days
        credit_limit (float): Maximum credit allowed
        created_at (datetime): Client creation timestamp
        is_active (bool): Client status
        user_id (int): Foreign key to User model
    
    Relationships:
        user: Many-to-One relationship with User model
        invoices: One-to-Many relationship with Invoice model
    
    Properties:
        total_purchases: Total amount of paid invoices
        outstanding_balance: Total amount of unpaid invoices
        credit_status: Current credit status based on limit
    """
    
    __tablename__ = 'clients'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    name = db.Column(db.String(120), nullable=False, index=True)
    contact_person = db.Column(db.String(100))
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    # Algerian Business Identifiers
    nif = db.Column(db.String(20), nullable=False)  # Numéro d'Identification Fiscale
    nis = db.Column(db.String(20), nullable=False)  # Numéro d'Identification Statistique
    rc = db.Column(db.String(20), nullable=False)   # Registre de Commerce
    art = db.Column(db.String(20), nullable=False)  # Article d'Imposition
    
    # Financial Information
    payment_terms = db.Column(db.Integer, default=30)  # Payment terms in days
    credit_limit = db.Column(db.Float, default=0.0)    # Maximum credit allowed
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('clients', lazy=True))
    invoices = db.relationship('Invoice', backref='client', lazy=True)
    
    @property
    def total_purchases(self):
        """
        Calculate total purchases amount from all paid invoices.
        
        Returns:
            float: Total amount of paid invoices
        """
        return sum(invoice.total_ttc for invoice in self.invoices if invoice.status == 'paid')
    
    @property
    def outstanding_balance(self):
        """
        Calculate outstanding balance from all unpaid invoices.
        
        Returns:
            float: Total amount of unpaid invoices
        """
        return sum(invoice.total_ttc for invoice in self.invoices if invoice.status == 'pending')
    
    @property
    def credit_status(self):
        """
        Check client's credit status based on credit limit.
        
        Returns:
            str: 'good', 'warning', or 'exceeded'
        """
        if self.credit_limit == 0:
            return 'good'
        
        usage_percent = (self.outstanding_balance / self.credit_limit) * 100
        if usage_percent < 75:
            return 'good'
        elif usage_percent < 90:
            return 'warning'
        else:
            return 'exceeded'
    
    def can_create_invoice(self, amount):
        """
        Check if a new invoice can be created based on credit limit.
        
        Args:
            amount (float): Amount of new invoice
            
        Returns:
            bool: True if invoice can be created, False otherwise
        """
        if self.credit_limit == 0:
            return True
        return (self.outstanding_balance + amount) <= self.credit_limit
    
    def get_overdue_invoices(self):
        """
        Get list of overdue invoices.
        
        Returns:
            list: List of overdue Invoice objects
        """
        return [invoice for invoice in self.invoices 
                if invoice.status == 'pending' and invoice.is_overdue]
    
    def __repr__(self):
        return f'<Client {self.name}>'
