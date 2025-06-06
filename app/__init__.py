from flask import Flask
import os

def create_app():
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Load configuration
    try:
        from .config import Config
        app.config.from_object(Config)
    except ImportError:
        # Fallback to root config
        import config
        app.secret_key = config.SECRET_KEY
        app.config['DEBUG'] = config.DEBUG
    
    # Ensure required directories exist
    os.makedirs('logs', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    # Register blueprints
    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.history import history_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(history_bp, url_prefix='/api')
    
    return app
