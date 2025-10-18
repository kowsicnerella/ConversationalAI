"""
AI Content Cache Model
Stores AI-generated content to avoid repeated expensive API calls
"""
from datetime import datetime
import hashlib
import json
from app.models import db


class AIContentCache(db.Model):
    """
    Cache for AI-generated content to reduce costs and improve response times
    """
    __tablename__ = "ai_content_cache"

    id = db.Column(db.Integer, primary_key=True)
    
    # Cache key identification
    content_type = db.Column(db.String(50), nullable=False, index=True)  # e.g., 'assessment', 'activity', 'lesson'
    input_hash = db.Column(db.String(64), nullable=False, unique=True, index=True)  # SHA256 hash of input params
    input_params = db.Column(db.JSON, nullable=False)  # Store original input for reference
    
    # Generated content
    generated_content = db.Column(db.Text, nullable=False)  # JSON string of generated content
    content_format = db.Column(db.String(20), default='json')  # 'json', 'text', 'markdown'
    
    # Metadata
    provider_used = db.Column(db.String(20), nullable=False)  # 'gemini', 'custom', 'openai'
    model_used = db.Column(db.String(100))  # Specific model name
    tokens_used = db.Column(db.Integer)  # Token count for cost tracking
    generation_time_ms = db.Column(db.Integer)  # Time taken to generate
    
    # Usage tracking
    hit_count = db.Column(db.Integer, default=0)  # Number of times this cache was used
    last_hit_at = db.Column(db.DateTime)  # Last time cache was accessed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime)  # Optional expiration
    
    # Quality metrics
    was_validated = db.Column(db.Boolean, default=False)  # Was content manually validated?
    validation_score = db.Column(db.Float)  # Optional quality score
    user_feedback_count = db.Column(db.Integer, default=0)  # Number of users who used this
    
    # Indexes for fast lookup
    __table_args__ = (
        db.Index('idx_content_type_hash', 'content_type', 'input_hash'),
        db.Index('idx_provider_created', 'provider_used', 'created_at'),
        db.Index('idx_hit_count', 'hit_count'),
    )

    @staticmethod
    def generate_cache_key(content_type: str, input_params: dict) -> str:
        """
        Generate a unique cache key from content type and input parameters
        
        Args:
            content_type: Type of content (e.g., 'assessment_questions')
            input_params: Dictionary of input parameters
            
        Returns:
            SHA256 hash string
        """
        # Sort dict keys for consistent hashing
        sorted_params = json.dumps(input_params, sort_keys=True)
        combined = f"{content_type}:{sorted_params}"
        return hashlib.sha256(combined.encode()).hexdigest()

    @staticmethod
    def get_cached_content(content_type: str, input_params: dict):
        """
        Retrieve cached content if available
        
        Args:
            content_type: Type of content to retrieve
            input_params: Input parameters used to generate content
            
        Returns:
            AIContentCache object or None
        """
        cache_key = AIContentCache.generate_cache_key(content_type, input_params)
        cache_entry = AIContentCache.query.filter_by(
            content_type=content_type,
            input_hash=cache_key
        ).first()
        
        if cache_entry:
            # Update hit tracking
            cache_entry.hit_count += 1
            cache_entry.last_hit_at = datetime.utcnow()
            db.session.commit()
            
        return cache_entry

    @staticmethod
    def cache_content(
        content_type: str,
        input_params: dict,
        generated_content: str,
        provider_used: str,
        model_used: str = None,
        tokens_used: int = None,
        generation_time_ms: int = None,
        content_format: str = 'json',
        expires_at: datetime = None
    ) -> 'AIContentCache':
        """
        Store generated content in cache
        
        Args:
            content_type: Type of content
            input_params: Input parameters used
            generated_content: The generated content (JSON string or text)
            provider_used: Provider used (gemini, custom, etc.)
            model_used: Specific model name
            tokens_used: Token count
            generation_time_ms: Generation time in milliseconds
            content_format: Format of content (json, text, markdown)
            expires_at: Optional expiration datetime
            
        Returns:
            AIContentCache object
        """
        cache_key = AIContentCache.generate_cache_key(content_type, input_params)
        
        # Check if already exists (update instead of create)
        existing = AIContentCache.query.filter_by(input_hash=cache_key).first()
        if existing:
            existing.generated_content = generated_content
            existing.provider_used = provider_used
            existing.model_used = model_used
            existing.tokens_used = tokens_used
            existing.generation_time_ms = generation_time_ms
            existing.created_at = datetime.utcnow()
            db.session.commit()
            return existing
        
        # Create new cache entry
        cache_entry = AIContentCache(
            content_type=content_type,
            input_hash=cache_key,
            input_params=input_params,
            generated_content=generated_content,
            content_format=content_format,
            provider_used=provider_used,
            model_used=model_used,
            tokens_used=tokens_used,
            generation_time_ms=generation_time_ms,
            expires_at=expires_at,
            hit_count=0
        )
        
        db.session.add(cache_entry)
        db.session.commit()
        return cache_entry

    @staticmethod
    def clear_expired():
        """Clear expired cache entries"""
        now = datetime.utcnow()
        expired = AIContentCache.query.filter(
            AIContentCache.expires_at.isnot(None),
            AIContentCache.expires_at < now
        ).delete()
        db.session.commit()
        return expired

    @staticmethod
    def get_cache_stats():
        """Get cache statistics"""
        total = AIContentCache.query.count()
        by_type = db.session.query(
            AIContentCache.content_type,
            db.func.count(AIContentCache.id).label('count'),
            db.func.sum(AIContentCache.hit_count).label('total_hits'),
            db.func.sum(AIContentCache.tokens_used).label('total_tokens')
        ).group_by(AIContentCache.content_type).all()
        
        by_provider = db.session.query(
            AIContentCache.provider_used,
            db.func.count(AIContentCache.id).label('count'),
            db.func.sum(AIContentCache.tokens_used).label('total_tokens')
        ).group_by(AIContentCache.provider_used).all()
        
        return {
            'total_entries': total,
            'by_type': [
                {
                    'type': item.content_type,
                    'entries': item.count,
                    'total_hits': item.total_hits or 0,
                    'tokens_saved': item.total_tokens or 0
                }
                for item in by_type
            ],
            'by_provider': [
                {
                    'provider': item.provider_used,
                    'entries': item.count,
                    'tokens_used': item.total_tokens or 0
                }
                for item in by_provider
            ]
        }

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'content_type': self.content_type,
            'input_hash': self.input_hash,
            'input_params': self.input_params,
            'generated_content': self.generated_content,
            'content_format': self.content_format,
            'provider_used': self.provider_used,
            'model_used': self.model_used,
            'tokens_used': self.tokens_used,
            'generation_time_ms': self.generation_time_ms,
            'hit_count': self.hit_count,
            'last_hit_at': self.last_hit_at.isoformat() if self.last_hit_at else None,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'was_validated': self.was_validated,
            'validation_score': self.validation_score,
            'user_feedback_count': self.user_feedback_count
        }
