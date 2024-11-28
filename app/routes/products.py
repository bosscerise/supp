from flask import render_template
from app.routes import products_bp

@products_bp.route('/')
def index():
    """Products listing page."""
    return render_template('products/index.html')
