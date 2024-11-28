from app import db
from datetime import datetime
from sqlalchemy.event import listens_for

class Product(db.Model):
    """
    Product Model for storing product information and inventory.
    
    This model represents products that suppliers sell to clients, including
    all necessary information for pricing, stock management, and profit calculation.
    
    Attributes:
        id (int): Primary key
        name (str): Product name
        description (str): Detailed product description
        reference (str): Unique product reference/code
        purchase_price (float): Price at which supplier buys the product
        selling_price (float): Price at which supplier sells the product
        stock (int): Current quantity in stock
        min_stock (int): Minimum stock level before alert
        category (str): Product category
        brand (str): Product brand/manufacturer
        created_at (datetime): Product creation timestamp
        updated_at (datetime): Last update timestamp
        is_active (bool): Product status (active/inactive)
        user_id (int): Foreign key to User model
    
    Relationships:
        user: Many-to-One relationship with User model
        invoice_items: One-to-Many relationship with InvoiceItem model
    
    Properties:
        margin: Calculated profit margin percentage
        profit: Calculated profit amount per unit
        total_value: Current stock value at purchase price
        total_potential_profit: Potential profit for current stock
    """
    
    __tablename__ = 'products'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    reference = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Financial Information
    purchase_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    
    # Inventory Information
    stock = db.Column(db.Integer, default=0)
    min_stock = db.Column(db.Integer, default=5)
    
    # Product Details
    category = db.Column(db.String(50))
    brand = db.Column(db.String(50))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('products', lazy=True))
    invoice_items = db.relationship('InvoiceItem', backref='product', lazy=True)
    
    @property
    def margin(self):
        """
        Calculate profit margin percentage.
        
        Returns:
            float: Profit margin as percentage
        """
        if self.purchase_price > 0:
            return ((self.selling_price - self.purchase_price) / self.purchase_price) * 100
        return 0
    
    @property
    def profit(self):
        """
        Calculate profit amount per unit.
        
        Returns:
            float: Profit amount per unit
        """
        return self.selling_price - self.purchase_price
    
    @property
    def total_value(self):
        """
        Calculate total value of current stock at purchase price.
        
        Returns:
            float: Total stock value
        """
        return self.stock * self.purchase_price
    
    @property
    def total_potential_profit(self):
        """
        Calculate potential profit for current stock.
        
        Returns:
            float: Total potential profit
        """
        return self.stock * self.profit
    
    def update_stock(self, quantity, operation='add'):
        """
        Update product stock.
        
        Args:
            quantity (int): Quantity to add or remove
            operation (str): 'add' or 'remove'
        
        Returns:
            bool: True if operation successful, False if insufficient stock
        """
        if operation == 'add':
            self.stock += quantity
            return True
        elif operation == 'remove':
            if self.stock >= quantity:
                self.stock -= quantity
                return True
            return False
        
    def __repr__(self):
        return f'<Product {self.reference}: {self.name}>'

@listens_for(Product, 'before_insert')
def generate_reference(mapper, connection, target):
    """
    Generate unique product reference if not provided.
    Format: PRD-YYYY-XXXXX
    """
    if not target.reference:
        year = datetime.utcnow().year
        last_product = Product.query.order_by(Product.id.desc()).first()
        last_id = last_product.id if last_product else 0
        target.reference = f'PRD-{year}-{str(last_id + 1).zfill(5)}'
