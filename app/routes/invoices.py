from flask import render_template
from app.routes import invoices_bp

@invoices_bp.route('/')
def index():
    """Invoices listing page."""
    return render_template('invoices/index.html')
