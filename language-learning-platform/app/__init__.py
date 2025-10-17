from flask import Flask, jsonify
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
from app.api.enhanced_question_routes import (
    enhanced_assessment_bp,
    enhanced_activity_bp,
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
    CORS(
        app,
        origins=["*"],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(chapter_bp, url_prefix="/api/chapters")
    app.register_blueprint(practice_bp, url_prefix="/api/practice")
    app.register_blueprint(test_bp, url_prefix="/api/tests")
    # Register learning path blueprint with explicit URL prefix
    app.register_blueprint(learning_path_bp, url_prefix="/api/learning-paths")
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
    app.register_blueprint(enhanced_activity_bp, url_prefix="/api/enhanced-activity")

    # Register vocabulary management blueprint
    app.register_blueprint(vocabulary_bp, url_prefix="/api/vocabulary")

    # Register notifications blueprint
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")

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

    # Register test auth blueprint (for debugging)
    app.register_blueprint(test_auth_bp, url_prefix="/api")

    # Also register with singular 'test' for alternative URL patterns
    app.register_blueprint(test_bp, url_prefix="/api/test", name="test_singular")

    # Register image-based learning blueprint
    from app.api.image_routes import image_bp

    app.register_blueprint(image_bp)

    # Health check endpoint
    @app.route("/health")
    def health_check():
        return {
            "status": "healthy",
            "message": "Telugu-English Learning Platform is running!",
        }

    return app
