"""
Activity Caching Service
Implements caching strategy to reduce API calls and improve performance.
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from functools import lru_cache
import json
import hashlib


class ActivityCache:
    """
    In-memory cache for generated activities.
    In production, this should use Redis or similar distributed cache.
    """
    
    def __init__(self, ttl_minutes: int = 30, max_size: int = 1000):
        """
        Initialize cache.
        
        Args:
            ttl_minutes: Time-to-live for cached items in minutes
            max_size: Maximum number of items to cache
        """
        self.cache = {}
        self.ttl = timedelta(minutes=ttl_minutes)
        self.max_size = max_size
        self.access_times = {}  # Track last access for LRU eviction
    
    def _generate_cache_key(
        self,
        user_id: int,
        activity_type: str,
        difficulty: float,
        **kwargs
    ) -> str:
        """
        Generate a unique cache key for the activity request.
        
        Args:
            user_id: User ID
            activity_type: Type of activity
            difficulty: Difficulty level
            **kwargs: Additional parameters
            
        Returns:
            Cache key string
        """
        # Create a deterministic key from parameters
        params = {
            'user_id': user_id,
            'activity_type': activity_type,
            'difficulty': round(difficulty, 2),
            **kwargs
        }
        
        # Sort keys for consistency
        params_str = json.dumps(params, sort_keys=True)
        
        # Hash for shorter key
        key_hash = hashlib.md5(params_str.encode()).hexdigest()
        
        return f"activity:{activity_type}:{user_id}:{key_hash}"
    
    def get(
        self,
        user_id: int,
        activity_type: str,
        difficulty: float,
        **kwargs
    ) -> Optional[Dict]:
        """
        Get cached activity if available and not expired.
        
        Args:
            user_id: User ID
            activity_type: Type of activity
            difficulty: Difficulty level
            **kwargs: Additional parameters
            
        Returns:
            Cached activity or None if not found/expired
        """
        key = self._generate_cache_key(user_id, activity_type, difficulty, **kwargs)
        
        if key not in self.cache:
            return None
        
        cached_item = self.cache[key]
        cached_time = cached_item['cached_at']
        
        # Check if expired
        if datetime.utcnow() - cached_time > self.ttl:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            return None
        
        # Update access time
        self.access_times[key] = datetime.utcnow()
        
        # Return a copy to prevent mutations affecting cache
        return cached_item['data'].copy()
    
    def set(
        self,
        user_id: int,
        activity_type: str,
        difficulty: float,
        activity_data: Dict,
        **kwargs
    ):
        """
        Cache an activity.
        
        Args:
            user_id: User ID
            activity_type: Type of activity
            difficulty: Difficulty level
            activity_data: Activity to cache
            **kwargs: Additional parameters
        """
        key = self._generate_cache_key(user_id, activity_type, difficulty, **kwargs)
        
        # Evict oldest items if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        self.cache[key] = {
            'data': activity_data.copy(),
            'cached_at': datetime.utcnow()
        }
        self.access_times[key] = datetime.utcnow()
    
    def _evict_lru(self):
        """Evict least recently used item."""
        if not self.access_times:
            return
        
        # Find least recently accessed key
        lru_key = min(self.access_times, key=self.access_times.get)
        
        del self.cache[lru_key]
        del self.access_times[lru_key]
    
    def invalidate_user_cache(self, user_id: int):
        """
        Invalidate all cached activities for a user.
        Useful when user's profile or progress changes significantly.
        
        Args:
            user_id: User ID
        """
        keys_to_delete = []
        user_prefix = f"activity:*:{user_id}:"
        
        for key in self.cache.keys():
            if f":{user_id}:" in key:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
    
    def clear(self):
        """Clear entire cache."""
        self.cache.clear()
        self.access_times.clear()
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'ttl_minutes': self.ttl.total_seconds() / 60,
            'utilization': len(self.cache) / self.max_size if self.max_size > 0 else 0
        }


# Global cache instance
activity_cache = ActivityCache(ttl_minutes=30, max_size=1000)


def cached_activity_generation(func):
    """
    Decorator to cache activity generation results.
    
    Usage:
        @cached_activity_generation
        def generate_some_activity(...):
            ...
    """
    def wrapper(
        user_id: int,
        activity_type: str = None,
        difficulty: float = 0.5,
        **kwargs
    ):
        # Try to get from cache
        cached = activity_cache.get(
            user_id=user_id,
            activity_type=activity_type,
            difficulty=difficulty,
            **kwargs
        )
        
        if cached:
            cached['from_cache'] = True
            return cached
        
        # Generate new activity
        result = func(
            user_id=user_id,
            activity_type=activity_type,
            difficulty=difficulty,
            **kwargs
        )
        
        # Cache the result
        if result and 'error' not in result:
            activity_cache.set(
                user_id=user_id,
                activity_type=activity_type,
                difficulty=difficulty,
                activity_data=result,
                **kwargs
            )
        
        result['from_cache'] = False
        return result
    
    return wrapper


@lru_cache(maxsize=100)
def get_user_context_cached(user_id: int, cache_key: str) -> Dict:
    """
    Cached user context lookup.
    cache_key should be based on user's last update timestamp.
    
    This uses Python's built-in LRU cache for simple in-process caching.
    """
    from app.services.content_generation_engine import ContentGenerationEngine
    engine = ContentGenerationEngine()
    return engine._get_user_context(user_id)


def get_cache_stats() -> Dict:
    """Get current cache statistics."""
    return activity_cache.get_stats()


def clear_cache():
    """Clear all caches."""
    activity_cache.clear()
    get_user_context_cached.cache_clear()
