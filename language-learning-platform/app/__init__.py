
from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.models import db
from app.api.auth_routes import auth_bp
from app.api.user_routes import user_bp
from app.api.activity_routes import activity_bp
from app.api.gamification_routes import gamification_bp
from app.api.personalization_routes import personalization_bp
from app.api.chat_routes import chat_bp
from app.api.course_routes import courses_bp
from app.api.media_routes import media_bp
from app.api.analytics_routes import analytics_bp
from app.api.chapter_routes import chapter_bp
from app.api.practice_routes import practice_bp
from app.api.test_routes import test_bp
from app.api.learning_path_routes import learning_path_bp
from app.api.adaptive_routes import adaptive_routes
from app.api.assessment_routes import assessment_routes
from app.api.enhanced_analytics_routes import analytics_bp as enhanced_analytics_bp
from app.api.enhanced_question_routes import enhanced_assessment_bp, enhanced_activity_bp
from app.api.vocabulary_routes import vocabulary_bp
from app.api.notifications_routes import notifications_bp
from config import config

migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Configure CORS to allow frontend requests
    CORS(app, origins=["*"], 
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(activity_bp, url_prefix='/api/activity')
    app.register_blueprint(gamification_bp, url_prefix='/api/gamification')
    app.register_blueprint(personalization_bp, url_prefix='/api/personalization')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(courses_bp, url_prefix='/api/courses')
    app.register_blueprint(media_bp, url_prefix='/api/media')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(chapter_bp, url_prefix='/api/chapters')
    app.register_blueprint(practice_bp, url_prefix='/api/practice')
    app.register_blueprint(test_bp, url_prefix='/api/tests')
    app.register_blueprint(learning_path_bp, url_prefix='/api/learning-paths')
    app.register_blueprint(adaptive_routes)
    app.register_blueprint(assessment_routes)
    
    # Register new adaptive learning blueprint
    from app.api.adaptive_learning_routes import adaptive_learning_bp
    app.register_blueprint(adaptive_learning_bp, url_prefix='/api/adaptive')
    
    # Register enhanced analytics and question analysis blueprints
    app.register_blueprint(enhanced_analytics_bp, url_prefix='/api/enhanced-analytics')
    app.register_blueprint(enhanced_assessment_bp, url_prefix='/api/enhanced-assessment')
    app.register_blueprint(enhanced_activity_bp, url_prefix='/api/enhanced-activity')
    
    # Register vocabulary management blueprint
    app.register_blueprint(vocabulary_bp, url_prefix='/api/vocabulary')
    
    # Register notifications blueprint
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    
    # Also register with singular 'test' for alternative URL patterns
    app.register_blueprint(test_bp, url_prefix='/api/test', name='test_singular')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Telugu-English Learning Platform is running!'}
    
    return app
