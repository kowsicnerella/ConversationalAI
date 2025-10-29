from flask import Flask, jsonify, request
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
from app.api.analytics_routes import analytics_bp as analytics_v1_bp
from app.api.chapter_routes import chapter_bp
from app.api.practice_routes import practice_bp
from app.api.test_routes import test_bp
from app.api.learning_path_routes import learning_path_bp
from app.routes.learning_path_routes import learning_path_bp as ai_learning_path_bp  # NEW AI-personalized routes
from app.routes.chat_routes import chat_bp as enhanced_chat_routes_bp  # NEW Enhanced Chat Routes V2
from app.api.adaptive_routes import adaptive_routes
from app.api.assessment_routes import assessment_routes
from app.api.enhanced_analytics_routes import analytics_bp as enhanced_analytics_bp
from app.api.enhanced_question_routes import (
    enhanced_assessment_bp,
    enhanced_activity_bp as enhanced_activity_v1_bp,
)
from app.api.vocabulary_routes import vocabulary_bp
from app.api.notifications_routes import notifications_bp
from app.api.test_auth_routes import test_auth_bp
from app.api.onboarding_routes import onboarding_bp
from app.api.lesson_routes import lesson_bp
from app.api.activities_routes import activities_bp
from app.api.chat_tutor_routes import chat_tutor_bp
from app.api.goals_routes import goals_bp
from app.api.enhanced_chat_routes import enhanced_chat_bp
from app.api.user_status_routes import user_status_bp
from app.routes.analytics_routes import analytics_bp as new_analytics_bp  # NEW Phase 2 Analytics
from app.routes.enhanced_activity_routes import enhanced_activity_bp as enhanced_activity_v2_bp  # Phase 2 Enhanced Activity Generation
from app.routes.content_generation_routes import content_generation_bp  # Phase 2 Complete Content Generation
from app.routes.activity_history_routes import activity_history_bp  # Phase 2 Activity History Tracking
from app.routes.performance_routes import performance_bp  # Phase 4 Performance Tracking
from app.routes.vocabulary_routes import vocabulary_bp as vocabulary_phase5_bp  # Phase 5 Vocabulary Mastery
from app.routes.assessment_routes import assessment_bp  # Phase 6 Intelligent Assessment
from app.routes.learning_analytics_routes import learning_analytics_bp  # Phase 7 Learning Analytics & Insights
from app.routes.gamification_routes import gamification_bp as gamification_phase9_bp  # Phase 9 Enhanced Gamification
from config import config

migrate = Migrate()
jwt = JWTManager()


def create_app(config_name="development"):
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # JWT Error Handlers for better debugging
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return (
            jsonify(
                {
                    "error": "Invalid token",
                    "message": error_string,
                    "telugu_message": "చెల్లని టోకెన్",
                }
            ),
            422,
        )

    @jwt.unauthorized_loader
    def unauthorized_callback(error_string):
        return (
            jsonify(
                {
                    "error": "Missing Authorization Header",
                    "message": error_string,
                    "telugu_message": "అధికార శీర్షిక లేదు",
                }
            ),
            401,
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "error": "Token has expired",
                    "message": "Please log in again",
                    "telugu_message": "టోకెన్ గడువు ముగిసింది. దయచేసి మళ్లీ లాగిన్ అవ్వండి",
                }
            ),
            401,
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "error": "Token has been revoked",
                    "message": "Please log in again",
                    "telugu_message": "టోకెన్ రద్దు చేయబడింది",
                }
            ),
            401,
        )

    # Configure CORS to allow frontend requests
    # Must be configured BEFORE registering blueprints
    # NOTE: Cannot use wildcard (*) with supports_credentials=True
    # For development with credentials, specify explicit origins
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5173",
    ]
    
    CORS(
        app,
        resources={r"/api/*": {
            "origins": allowed_origins,
            "allow_headers": ["Content-Type", "Authorization"],
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "supports_credentials": True,
            "max_age": 3600
        }},
        automatic_options=True,
    )

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(activity_bp, url_prefix="/api/activity")
    app.register_blueprint(gamification_bp, url_prefix="/api/gamification")
    app.register_blueprint(personalization_bp, url_prefix="/api/personalization")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(courses_bp, url_prefix="/api/courses")
    app.register_blueprint(media_bp, url_prefix="/api/media")
    app.register_blueprint(analytics_v1_bp, url_prefix="/api/analytics")
    app.register_blueprint(chapter_bp, url_prefix="/api/chapters")
    app.register_blueprint(practice_bp, url_prefix="/api/practice")
    app.register_blueprint(test_bp, url_prefix="/api/tests")
    # Register learning path blueprint with explicit URL prefix
    app.register_blueprint(learning_path_bp, url_prefix="/api/learning-paths")
    # Register AI-powered personalized learning path blueprint
    app.register_blueprint(ai_learning_path_bp)  # Uses /api/learning-path prefix from blueprint definition
    app.register_blueprint(adaptive_routes)
    app.register_blueprint(assessment_routes)

    # Register new adaptive learning blueprint
    from app.api.adaptive_learning_routes import adaptive_learning_bp

    app.register_blueprint(adaptive_learning_bp, url_prefix="/api/adaptive")

    # Register enhanced analytics and question analysis blueprints
    app.register_blueprint(enhanced_analytics_bp, url_prefix="/api/enhanced-analytics")
    app.register_blueprint(
        enhanced_assessment_bp, url_prefix="/api/enhanced-assessment"
    )
    app.register_blueprint(enhanced_activity_v1_bp, url_prefix="/api/enhanced-activity")

    # Register vocabulary management blueprint (old API routes - for backward compatibility with /words endpoint)
    app.register_blueprint(vocabulary_bp, url_prefix="/api/vocabulary")

    # Register notifications blueprint
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")

    # Register user status and navigation guard blueprint
    app.register_blueprint(user_status_bp, url_prefix="/api")

    # Register onboarding workflow blueprint
    app.register_blueprint(onboarding_bp, url_prefix="/api/onboarding")

    # Register lesson completion and review blueprint
    app.register_blueprint(lesson_bp, url_prefix="/api/lesson")

    # Register activities blueprint for quiz and flashcard generation
    app.register_blueprint(activities_bp, url_prefix="/api/activities")

    # Register chat tutor blueprint for AI tutoring conversations
    app.register_blueprint(chat_tutor_bp)  # Already has url_prefix in blueprint

    # Register enhanced chat with Mem0 integration
    app.register_blueprint(enhanced_chat_bp, url_prefix="/api/enhanced-chat")

    # Register goals and milestones blueprint for achievement tracking
    app.register_blueprint(goals_bp)  # Already has url_prefix in blueprint

    # Register NEW Phase 2 Analytics endpoints
    app.register_blueprint(new_analytics_bp, url_prefix="/api/analytics-v2")
    
    # Register NEW Phase 2 Enhanced Activity Generation endpoints
    app.register_blueprint(enhanced_activity_v2_bp, url_prefix="/api/activities-v2")
    
    # Register NEW Phase 2 Complete Content Generation Engine
    app.register_blueprint(content_generation_bp)  # Already has url_prefix
    
    # Register NEW Phase 2 Activity History Tracking
    app.register_blueprint(activity_history_bp)  # Already has url_prefix
    
    # Register NEW Phase 4 Performance Tracking
    app.register_blueprint(performance_bp, url_prefix="/api/performance")
    
    # Register NEW Phase 5 Vocabulary Mastery (SM-2 spaced repetition)
    app.register_blueprint(vocabulary_phase5_bp, url_prefix="/api/vocabulary-v2")
    
    # Register NEW Phase 6 Intelligent Assessment System
    app.register_blueprint(assessment_bp, url_prefix="/api/intelligent-assessment")
    
    # Register NEW Phase 7 Learning Analytics & Insights
    app.register_blueprint(learning_analytics_bp)  # Already has url_prefix in blueprint
    
    # Register NEW Phase 9 Enhanced Gamification & Motivation System
    app.register_blueprint(gamification_phase9_bp)  # Already has url_prefix in blueprint
    
    # Register NEW Enhanced Chat Routes V2 with Mem0, Web Search, and Vector DB
    app.register_blueprint(enhanced_chat_routes_bp, url_prefix="/api/chat-v2", name="enhanced_chat_v2")

    # Register test auth blueprint (for debugging)
    app.register_blueprint(test_auth_bp, url_prefix="/api")

    # Also register with singular 'test' for alternative URL patterns
    app.register_blueprint(test_bp, url_prefix="/api/test", name="test_singular")

    # Register image-based learning blueprint
    from app.api.image_routes import image_bp

    app.register_blueprint(image_bp)

    # Global handler for OPTIONS requests (CORS preflight)
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify({"status": "ok"})
            response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
            response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,PATCH,OPTIONS")
            response.headers.add("Access-Control-Allow-Credentials", "true")
            response.status_code = 200
            return response

    # Health check endpoint
    @app.route("/health")
    def health_check():
        
        return {
            "status": "healthy",
            "message": "Telugu-English Learning Platform is running!",
        }

    return app
