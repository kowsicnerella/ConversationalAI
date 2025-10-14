"""
Mem0 Integration Service
Manages user knowledge and context using Mem0 for personalized learning experiences.
"""

import sys
import os
from datetime import datetime
import json
from typing import Dict, List, Optional, Any


class Mem0Service:
    """
    Service for managing user knowledge, preferences, and learning context using Mem0.
    Lazy loads mem0 configuration to avoid import errors.
    """
    
    def __init__(self):
        self._memory = None
        self._initialized = False
    
    @property
    def memory(self):
        """Lazy load memory agent on first access."""
        if not self._initialized:
            try:
                # Add parent directory to path to import mem0_config
                # Navigate from app/services/ -> app/ -> language-learning-platform/
                current_dir = os.path.dirname(os.path.abspath(__file__))
                language_learning_dir = os.path.dirname(os.path.dirname(current_dir))
                sys.path.insert(0, language_learning_dir)
                
                try:
                    from mem0_config import memory_agent
                    self._memory = memory_agent
                except ImportError:
                    # If mem0_config is not found, try to import from root directory
                    root_dir = os.path.dirname(language_learning_dir)
                    sys.path.insert(0, root_dir)
                    from mem0_config import memory_agent
                    self._memory = memory_agent
                
                self._initialized = True
            except Exception as e:
                print(f"Warning: Mem0 not available: {e}")
                print("Mem0 features will be disabled. Set up Weaviate and Google AI to enable.")
                self._memory = None
                self._initialized = True
        return self._memory
    
    def is_available(self):
        """Check if Mem0 is available and configured."""
        return self.memory is not None
    
    def add_user_interaction(
        self, 
        user_id: int, 
        message: str, 
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a user interaction to memory.
        
        Args:
            user_id: User ID
            message: User message or interaction content
            context: Additional context (activity type, proficiency level, etc.)
            metadata: Additional metadata to store
            
        Returns:
            Result of memory addition
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Mem0 not configured",
                "message": "Memory service is not available"
            }
        
        try:
            # Prepare enriched message with context
            enriched_context = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": str(user_id),
                **(context or {})
            }
            
            # Add to memory
            result = self.memory.add(
                messages=message,
                user_id=str(user_id),
                metadata={
                    **enriched_context,
                    **(metadata or {})
                }
            )
            
            return {
                "success": True,
                "result": result,
                "message": "Interaction saved to memory"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to save interaction to memory"
            }
    
    def get_user_memories(
        self, 
        user_id: int, 
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve user memories from Mem0.
        
        Args:
            user_id: User ID
            limit: Maximum number of memories to retrieve
            filters: Optional filters for memory retrieval
            
        Returns:
            List of memories
        """
        if not self.is_available():
            return []
        
        try:
            memories = self.memory.get_all(
                user_id=str(user_id),
                limit=limit
            )
            
            return memories if memories else []
        except Exception as e:
            print(f"Error retrieving memories: {e}")
            return []
    
    def search_user_memories(
        self, 
        query: str, 
        user_id: int, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search user memories using semantic search.
        
        Args:
            query: Search query
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of relevant memories
        """
        if not self.is_available():
            return []
        
        try:
            results = self.memory.search(
                query=query,
                user_id=str(user_id),
                limit=limit
            )
            
            return results if results else []
        except Exception as e:
            print(f"Error searching memories: {e}")
            return []
    
    def update_user_memory(
        self, 
        memory_id: str, 
        user_id: int, 
        updated_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing memory.
        
        Args:
            memory_id: Memory ID to update
            user_id: User ID
            updated_data: Updated memory data
            
        Returns:
            Update result
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Mem0 not configured",
                "message": "Memory service is not available"
            }
        
        try:
            result = self.memory.update(
                memory_id=memory_id,
                data=updated_data
            )
            
            return {
                "success": True,
                "result": result,
                "message": "Memory updated successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update memory"
            }
    
    def delete_user_memory(
        self, 
        memory_id: str, 
        user_id: int
    ) -> Dict[str, Any]:
        """
        Delete a specific memory.
        
        Args:
            memory_id: Memory ID to delete
            user_id: User ID
            
        Returns:
            Deletion result
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Mem0 not configured",
                "message": "Memory service is not available"
            }
        
        try:
            result = self.memory.delete(memory_id=memory_id)
            
            return {
                "success": True,
                "result": result,
                "message": "Memory deleted successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to delete memory"
            }
    
    def get_user_context_for_conversation(
        self, 
        user_id: int,
        conversation_type: str = "chat",
        recent_limit: int = 5
    ) -> Dict[str, Any]:
        """
        Get comprehensive user context for AI conversations.
        
        Args:
            user_id: User ID
            conversation_type: Type of conversation (chat, practice, role_play, etc.)
            recent_limit: Number of recent memories to include
            
        Returns:
            User context dictionary with preferences, history, and relevant memories
        """
        try:
            # Get recent memories
            recent_memories = self.get_user_memories(user_id, limit=recent_limit)
            
            # Search for relevant learning preferences
            preference_queries = [
                "learning goals and preferences",
                "strengths and weaknesses",
                "favorite topics and interests",
                "common mistakes and challenges"
            ]
            
            relevant_context = {}
            for query in preference_queries:
                results = self.search_user_memories(query, user_id, limit=2)
                if results:
                    key = query.replace(" ", "_")
                    relevant_context[key] = results
            
            return {
                "recent_memories": recent_memories,
                "relevant_context": relevant_context,
                "conversation_type": conversation_type,
                "retrieved_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error getting user context: {e}")
            return {
                "recent_memories": [],
                "relevant_context": {},
                "conversation_type": conversation_type,
                "error": str(e)
            }
    
    def save_learning_achievement(
        self, 
        user_id: int, 
        achievement_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save a learning achievement or milestone to memory.
        
        Args:
            user_id: User ID
            achievement_data: Achievement details (type, description, points, etc.)
            
        Returns:
            Save result
        """
        achievement_message = f"User achieved: {achievement_data.get('description', 'New achievement')}"
        
        return self.add_user_interaction(
            user_id=user_id,
            message=achievement_message,
            context={
                "type": "achievement",
                "achievement_type": achievement_data.get("type"),
                "points_earned": achievement_data.get("points", 0)
            },
            metadata=achievement_data
        )
    
    def save_mistake_pattern(
        self, 
        user_id: int, 
        mistake_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save a mistake pattern for future reference and practice.
        
        Args:
            user_id: User ID
            mistake_data: Mistake details (type, original, corrected, explanation)
            
        Returns:
            Save result
        """
        mistake_message = f"User made a {mistake_data.get('mistake_type', 'grammar')} mistake: {mistake_data.get('original_text', '')}. Correct form: {mistake_data.get('corrected_text', '')}. {mistake_data.get('explanation', '')}"
        
        return self.add_user_interaction(
            user_id=user_id,
            message=mistake_message,
            context={
                "type": "mistake_pattern",
                "mistake_category": mistake_data.get("mistake_category")
            },
            metadata=mistake_data
        )
    
    def save_vocabulary_learning(
        self, 
        user_id: int, 
        vocabulary_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save vocabulary learning to memory.
        
        Args:
            user_id: User ID
            vocabulary_data: Vocabulary details (word, translation, context, etc.)
            
        Returns:
            Save result
        """
        vocab_message = f"User learned the word '{vocabulary_data.get('english_word', '')}' which means '{vocabulary_data.get('telugu_translation', '')}' in Telugu. Context: {vocabulary_data.get('context_sentence', '')}"
        
        return self.add_user_interaction(
            user_id=user_id,
            message=vocab_message,
            context={
                "type": "vocabulary",
                "difficulty_level": vocabulary_data.get("difficulty_level"),
                "category": vocabulary_data.get("category")
            },
            metadata=vocabulary_data
        )
    
    def save_user_preference(
        self, 
        user_id: int, 
        preference_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save user learning preferences.
        
        Args:
            user_id: User ID
            preference_data: Preference details
            
        Returns:
            Save result
        """
        pref_message = f"User preference: {json.dumps(preference_data)}"
        
        return self.add_user_interaction(
            user_id=user_id,
            message=pref_message,
            context={
                "type": "preference"
            },
            metadata=preference_data
        )
    
    def get_personalized_suggestions(
        self, 
        user_id: int,
        current_proficiency: str = "beginner"
    ) -> Dict[str, Any]:
        """
        Get personalized learning suggestions based on user's memory and context.
        
        Args:
            user_id: User ID
            current_proficiency: User's current proficiency level
            
        Returns:
            Personalized suggestions
        """
        try:
            # Search for areas needing improvement
            weakness_search = self.search_user_memories(
                "mistakes weaknesses struggles difficult",
                user_id,
                limit=5
            )
            
            # Search for strengths
            strength_search = self.search_user_memories(
                "achievements strengths good performance",
                user_id,
                limit=3
            )
            
            # Search for interests
            interest_search = self.search_user_memories(
                "interests topics preferences likes",
                user_id,
                limit=3
            )
            
            return {
                "weaknesses": weakness_search,
                "strengths": strength_search,
                "interests": interest_search,
                "proficiency_level": current_proficiency,
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error getting personalized suggestions: {e}")
            return {
                "weaknesses": [],
                "strengths": [],
                "interests": [],
                "error": str(e)
            }


# Singleton instance
mem0_service = Mem0Service()
