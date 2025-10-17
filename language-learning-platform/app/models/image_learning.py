"""
Image-Based Learning Models
Stores uploaded images and AI-identified objects for vocabulary learning
"""

from datetime import datetime
from .user import db


class ImageLearning(db.Model):
    """
    Model to store uploaded images and AI analysis results
    """

    __tablename__ = "image_learning"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Image storage
    image_filename = db.Column(db.String(255), nullable=False)  # Stored filename
    image_path = db.Column(db.String(500), nullable=False)  # Full path to stored image
    image_url = db.Column(db.String(500))  # URL to access image
    original_filename = db.Column(db.String(255))  # User's original filename
    file_size_bytes = db.Column(db.Integer)  # Image size in bytes
    image_format = db.Column(db.String(10))  # JPG, PNG, WEBP

    # Analysis metadata
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    analysis_status = db.Column(
        db.String(20), default="pending"
    )  # pending, completed, failed
    error_message = db.Column(db.Text)  # Error details if analysis failed

    # AI-identified objects (JSON format)
    # Format: [{
    #   "object_name_english": "Refrigerator",
    #   "object_name_telugu": "రెఫ్రిజరేటర్",
    #   "confidence": 0.95,
    #   "sample_sentence": "I keep milk in the refrigerator.",
    #   "sentence_telugu": "నేను రెఫ్రిజరేటర్ లో పాలు ఉంచుతాను.",
    #   "pronunciation": "re-fri-juh-rey-ter",
    #   "category": "kitchen_appliance"
    # }]
    identified_objects = db.Column(db.JSON, default=list)
    total_objects_found = db.Column(db.Integer, default=0)

    # User interaction tracking
    objects_saved_to_vocabulary = db.Column(
        db.JSON, default=list
    )  # List of saved object IDs
    flashcard_session_created = db.Column(db.Boolean, default=False)
    flashcard_session_id = db.Column(
        db.Integer, db.ForeignKey("learning_sessions.id"), nullable=True
    )

    # Device/source information
    uploaded_from_device = db.Column(db.String(50))  # mobile, desktop, tablet
    is_camera_capture = db.Column(
        db.Boolean, default=False
    )  # True if from camera, False if file upload

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user = db.relationship(
        "User", backref="image_learning_sessions", foreign_keys=[user_id]
    )
    flashcard_session = db.relationship(
        "LearningSession", backref="source_image", foreign_keys=[flashcard_session_id]
    )

    def to_dict(self):
        """Convert ImageLearning to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "image_filename": self.image_filename,
            "image_url": self.image_url,
            "original_filename": self.original_filename,
            "file_size_bytes": self.file_size_bytes,
            "file_size_mb": (
                round(self.file_size_bytes / (1024 * 1024), 2)
                if self.file_size_bytes
                else None
            ),
            "image_format": self.image_format,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
            "analysis_status": self.analysis_status,
            "error_message": self.error_message,
            "identified_objects": self.identified_objects,
            "total_objects_found": self.total_objects_found,
            "objects_saved_to_vocabulary": self.objects_saved_to_vocabulary,
            "flashcard_session_created": self.flashcard_session_created,
            "flashcard_session_id": self.flashcard_session_id,
            "uploaded_from_device": self.uploaded_from_device,
            "is_camera_capture": self.is_camera_capture,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<ImageLearning {self.id}: User {self.user_id}, {self.total_objects_found} objects>"


class ImageObjectVocabulary(db.Model):
    """
    Model to track which image objects were saved as vocabulary words
    Links ImageLearning to VocabularyWord
    """

    __tablename__ = "image_object_vocabulary"

    id = db.Column(db.Integer, primary_key=True)
    image_learning_id = db.Column(
        db.Integer, db.ForeignKey("image_learning.id"), nullable=False
    )
    vocabulary_word_id = db.Column(
        db.Integer, db.ForeignKey("vocabulary_words.id"), nullable=False
    )

    # Which object from the identified_objects array (by index or name)
    object_index = db.Column(db.Integer)  # Index in identified_objects array
    object_name_english = db.Column(db.String(200))  # Store for quick reference

    saved_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    image_learning = db.relationship("ImageLearning", backref="vocabulary_links")
    vocabulary_word = db.relationship("VocabularyWord", backref="source_images")

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "image_learning_id": self.image_learning_id,
            "vocabulary_word_id": self.vocabulary_word_id,
            "object_index": self.object_index,
            "object_name_english": self.object_name_english,
            "saved_at": self.saved_at.isoformat() if self.saved_at else None,
        }

    def __repr__(self):
        return f"<ImageObjectVocabulary {self.id}: Image {self.image_learning_id} -> Vocab {self.vocabulary_word_id}>"
