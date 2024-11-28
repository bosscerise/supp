from app import db
from datetime import datetime
from sqlalchemy.event import listens_for

class Transaction(db.Model):
    """
    Transaction Model for storing payment transactions.
    
    This model represents payment transactions made by clients for invoices,
    including payment method and reference information.
    
    Attributes:
        id (int): Primary key
        date (datetime): Transaction date
        amount (float): Payment amount
        payment_method (str): Method of payment (cash, check, bank_transfer)
        reference (str): Payment reference (check number, transfer reference)
        bank_name (str): Bank name for checks and transfers
        check_date (datetime): Date on check if payment by check
        notes (str): Additional transaction notes
        status (str): Transaction status (pending, completed, rejected)
        
        # Foreign Keys
        invoice_id (int): Foreign key to Invoice model
        user_id (int): Foreign key to User model
        
    Relationships:
        invoice: Many-to-One relationship with Invoice model
        user: Many-to-One relationship with User model
    """
    
    __tablename__ = 'transactions'
    
    PAYMENT_METHODS = ['cash', 'check', 'bank_transfer']
    STATUS_TYPES = ['pending', 'completed', 'rejected']
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Transaction Information
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    reference = db.Column(db.String(100))
    
    # Bank Information (for checks and transfers)
    bank_name = db.Column(db.String(100))
    check_date = db.Column(db.DateTime)
    
    # Additional Information
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))
    
    def __init__(self, **kwargs):
        """Initialize transaction with validation"""
        super(Transaction, self).__init__(**kwargs)
        if self.payment_method not in self.PAYMENT_METHODS:
            raise ValueError(f"Invalid payment method. Must be one of: {', '.join(self.PAYMENT_METHODS)}")
    
    def validate(self):
        """
        Validate transaction data based on payment method.
        
        Returns:
            bool: True if valid, False otherwise
        """
        if self.payment_method == 'check':
            return bool(self.bank_name and self.check_date and self.reference)
        elif self.payment_method == 'bank_transfer':
            return bool(self.bank_name and self.reference)
        return True  # Cash payment doesn't need additional validation
    
    def complete(self):
        """Mark transaction as completed and update invoice"""
        if self.validate():
            self.status = 'completed'
            if self.invoice.amount_paid >= self.invoice.total_ttc:
                self.invoice.status = 'paid'
            elif self.invoice.amount_paid > 0:
                self.invoice.status = 'partial'
            db.session.commit()
            return True
        return False
    
    def reject(self, reason=None):
        """
        Mark transaction as rejected.
        
        Args:
            reason (str): Reason for rejection
        """
        self.status = 'rejected'
        if reason:
            self.notes = f"Rejected: {reason}"
        db.session.commit()
    
    @property
    def is_check_payment(self):
        """Check if payment is by check"""
        return self.payment_method == 'check'
    
    @property
    def is_bank_transfer(self):
        """Check if payment is by bank transfer"""
        return self.payment_method == 'bank_transfer'
    
    @property
    def is_cash(self):
        """Check if payment is by cash"""
        return self.payment_method == 'cash'
    
    def __repr__(self):
        return f'<Transaction {self.payment_method}: {self.amount}>'

@listens_for(Transaction, 'before_insert')
def generate_reference(mapper, connection, target):
    """
    Generate transaction reference if not provided.
    Format: PMT-YYYY-XXXXX
    """
    if not target.reference and target.payment_method != 'cash':
        year = datetime.utcnow().year
        last_transaction = Transaction.query.order_by(Transaction.id.desc()).first()
        last_id = last_transaction.id if last_transaction else 0
        target.reference = f'PMT-{year}-{str(last_id + 1).zfill(5)}'
