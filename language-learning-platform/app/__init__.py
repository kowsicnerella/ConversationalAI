
from flask import Flask
from flask_migrate import Migrate
from app.models import db
from app.api.auth_routes import auth_bp
from app.api.user_routes import user_bp
from app.api.activity_routes import activity_bp
from app.api.gamification_routes import gamification_bp
from app.api.personalization_routes import personalization_bp
from config import config

migrate = Migrate()

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(activity_bp, url_prefix='/api/activity')
    app.register_blueprint(gamification_bp, url_prefix='/api/gamification')
    app.register_blueprint(personalization_bp, url_prefix='/api/personalization')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Telugu-English Learning Platform is running!'}
    
    return app
