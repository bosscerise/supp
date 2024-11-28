from app import db
from datetime import datetime, timedelta
from sqlalchemy.event import listens_for

class InvoiceItem(db.Model):
    """
    InvoiceItem Model for storing individual items in an invoice.
    
    This model represents each product line in an invoice with its
    quantity and price information.
    
    Attributes:
        id (int): Primary key
        invoice_id (int): Foreign key to Invoice model
        product_id (int): Foreign key to Product model
        quantity (int): Quantity of product
        unit_price (float): Unit price at time of sale
        description (str): Optional item description
        
    Relationships:
        invoice: Many-to-One relationship with Invoice model
        product: Many-to-One relationship with Product model
        
    Properties:
        subtotal: Total amount for this item (quantity * unit_price)
    """
    
    __tablename__ = 'invoice_items'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Item Details
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    
    # Relationships
    product = db.relationship('Product')
    
    @property
    def subtotal(self):
        """Calculate subtotal for this item"""
        return self.quantity * self.unit_price
    
    def __repr__(self):
        return f'<InvoiceItem {self.product.name} x{self.quantity}>'

class Invoice(db.Model):
    """
    Invoice Model for storing invoice information.
    
    This model represents invoices issued to clients, including all financial
    calculations and tax information required by Algerian regulations.
    
    Attributes:
        id (int): Primary key
        invoice_number (str): Unique invoice number (FAC-YYYY-XXXXX)
        date (datetime): Invoice date
        due_date (datetime): Payment due date
        status (str): Invoice status (draft, validated, paid, cancelled)
        user_id (int): Foreign key to User model
        client_id (int): Foreign key to Client model
        
        # Financial Information
        total_ht (float): Total amount before taxes
        tva (float): TVA amount (19%)
        tap (float): TAP amount (2%)
        total_ttc (float): Total amount including taxes
        
    Relationships:
        user: Many-to-One relationship with User model
        client: Many-to-One relationship with Client model
        items: One-to-Many relationship with InvoiceItem model
        transactions: One-to-Many relationship with Transaction model
        
    Properties:
        amount_paid: Total amount paid
        amount_due: Remaining amount to be paid
        is_overdue: Whether payment is overdue
        payment_status: Current payment status
    """
    
    __tablename__ = 'invoices'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Invoice Information
    invoice_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='draft')  # draft, validated, paid, cancelled
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Financial Information
    total_ht = db.Column(db.Float, default=0.0)    # Total HT (without taxes)
    tva = db.Column(db.Float, default=0.0)         # TVA amount (19%)
    tap = db.Column(db.Float, default=0.0)         # TAP amount (2%)
    total_ttc = db.Column(db.Float, default=0.0)   # Total TTC (with taxes)
    
    # Additional Information
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True,
                          cascade='all, delete-orphan')
    user = db.relationship('User', backref=db.backref('invoices', lazy=True))
    transactions = db.relationship('Transaction', backref='invoice', lazy=True,
                                 cascade='all, delete-orphan')
    
    def calculate_totals(self):
        """
        Calculate all totals for the invoice including taxes.
        Updates total_ht, tva, tap, and total_ttc fields.
        """
        self.total_ht = sum(item.subtotal for item in self.items)
        self.tva = self.total_ht * 0.19  # 19% TVA
        self.tap = self.total_ht * 0.02  # 2% TAP
        self.total_ttc = self.total_ht + self.tva + self.tap
    
    def add_item(self, product, quantity):
        """
        Add a product to the invoice.
        
        Args:
            product (Product): Product to add
            quantity (int): Quantity to add
            
        Returns:
            InvoiceItem: Created invoice item
        """
        item = InvoiceItem(
            product=product,
            quantity=quantity,
            unit_price=product.selling_price
        )
        self.items.append(item)
        self.calculate_totals()
        return item
    
    @property
    def amount_paid(self):
        """Calculate total amount paid through transactions"""
        return sum(transaction.amount for transaction in self.transactions)
    
    @property
    def amount_due(self):
        """Calculate remaining amount to be paid"""
        return self.total_ttc - self.amount_paid
    
    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        if self.status != 'paid' and self.due_date:
            return datetime.utcnow() > self.due_date
        return False
    
    @property
    def payment_status(self):
        """
        Get current payment status.
        
        Returns:
            str: 'paid', 'partial', 'pending', or 'overdue'
        """
        if self.amount_paid >= self.total_ttc:
            return 'paid'
        elif self.amount_paid > 0:
            return 'partial'
        elif self.is_overdue:
            return 'overdue'
        return 'pending'
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'

@listens_for(Invoice, 'before_insert')
def set_invoice_number(mapper, connection, target):
    """
    Generate unique invoice number if not provided.
    Format: FAC-YYYY-XXXXX
    """
    if not target.invoice_number:
        year = datetime.utcnow().year
        last_invoice = Invoice.query.filter(
            Invoice.invoice_number.like(f'FAC-{year}-%')
        ).order_by(Invoice.id.desc()).first()
        
        if last_invoice:
            last_number = int(last_invoice.invoice_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
            
        target.invoice_number = f'FAC-{year}-{str(new_number).zfill(5)}'

@listens_for(Invoice, 'before_insert')
def set_due_date(mapper, connection, target):
    """Set due date based on client's payment terms if not provided"""
    if not target.due_date and target.client:
        target.due_date = target.date + timedelta(days=target.client.payment_terms)
