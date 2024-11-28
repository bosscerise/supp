import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'suppliers.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Algerian locale settings
    BABEL_DEFAULT_LOCALE = 'ar_DZ'
    BABEL_DEFAULT_TIMEZONE = 'Africa/Algiers'
    
    # Custom configurations
    INVOICE_PREFIX = 'FAC'
    PROFORMA_PREFIX = 'PRO'
    BON_COMMANDE_PREFIX = 'BC'
    BON_LIVRAISON_PREFIX = 'BL'
    
    # Tax rates
    TVA_RATE = 0.19  # 19% TVA
    TAP_RATE = 0.02  # 2% TAP