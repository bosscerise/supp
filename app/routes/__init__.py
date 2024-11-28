from flask import Blueprint

# Create blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
products_bp = Blueprint('products', __name__, url_prefix='/products')
clients_bp = Blueprint('clients', __name__, url_prefix='/clients')
invoices_bp = Blueprint('invoices', __name__, url_prefix='/invoices')

def init_app(app):
    """Register blueprints with the Flask application."""
    # Import views here to avoid circular imports
    from .auth import auth_bp
    from .main import main_bp
    from .products import products_bp
    from .clients import clients_bp
    from .invoices import invoices_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(invoices_bp)