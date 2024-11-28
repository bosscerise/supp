from flask import render_template
from app.routes import clients_bp

@clients_bp.route('/')
def index():
    """Clients listing page."""
    return render_template('clients/index.html')
