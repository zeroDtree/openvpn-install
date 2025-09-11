"""
OpenVPN Client Management Web Server Configuration
"""

import os

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this-in-production'
    DATABASE_PATH = 'ovpn_clients.db'
    
    # Server configuration
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('OPENVPN_WEB_PORT', 5000))
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # File path configuration
    CLIENT_FILES_DIR = '.'  # Base directory where client files are located
    CLIENT_FILE_PATTERN = 'clients_ovpn/client*.ovpn'  # Client file matching pattern
    
    # Security configuration
    SESSION_COOKIE_SECURE = False  # Should be set to True in production (requires HTTPS)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Default admin account
    DEFAULT_ADMIN_USERNAME = 'admin'
    DEFAULT_ADMIN_PASSWORD = 'admin123'  # Please change in production environment

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    HOST = '127.0.0.1'

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-secret-key-in-production'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
