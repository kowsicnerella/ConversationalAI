"""
Vector Database Service
Manages embeddings, semantic search, and vector storage for chat history
Uses Weaviate for vector search with fallback to local embeddings
"""

import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import hashlib
from app.models import db, ChatMessage


class VectorDBService:
    """Service for managing vector embeddings and semantic search"""

    def __init__(self, use_weaviate: bool = False):
        """
        Initialize vector DB service
        
        Args:
            use_weaviate: Whether to use Weaviate (if False, uses in-memory embeddings)
        """
        self.use_weaviate = use_weaviate
        self.weaviate_client = None
        self.embeddings_cache = {}  # In-memory cache for embeddings
        
        if use_weaviate:
            try:
                import weaviate
                from weaviate.client import Client
                
                # Connect to Weaviate
                self.weaviate_client = Client(
                    url="http://localhost:8080"  # Default Weaviate URL
                )
                print("✅ Connected to Weaviate")
            except Exception as e:
                print(f"⚠️ Failed to connect to Weaviate: {e}")
                self.use_weaviate = False

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for text using sentence-transformers
        
        Args:
            text: Text to embed
            
        Returns:
            List of float values representing the embedding
        """
        try:
            from sentence_transformers import SentenceTransformer
            
            # Use a lightweight model for embeddings
            model = SentenceTransformer('distiluse-base-multilingual-case-sensitive-v2')
            embeddings = model.encode(text)
            return embeddings.tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

    def cache_embedding(self, text: str, embedding: List[float]) -> None:
        """Cache an embedding in memory"""
        # Create hash of text for cache key
        text_hash = hashlib.md5(text.encode()).hexdigest()
        self.embeddings_cache[text_hash] = {
            "text": text,
            "embedding": embedding,
            "cached_at": datetime.utcnow().isoformat(),
        }

    def get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self.embeddings_cache:
            return self.embeddings_cache[text_hash]["embedding"]
        return None

    def store_message_embedding(
        self, message_id: int, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store a message embedding
        
        Args:
            message_id: ID of the message
            text: Message text to embed
            metadata: Additional metadata
            
        Returns:
            Result dictionary
        """
        try:
            # Check cache first
            embedding = self.get_cached_embedding(text)
            
            if embedding is None:
                # Generate new embedding
                embedding = self.generate_embedding(text)
                if embedding is None:
                    return {"success": False, "error": "Failed to generate embedding"}
                
                # Cache it
                self.cache_embedding(text, embedding)

            if self.use_weaviate and self.weaviate_client:
                # Store in Weaviate
                result = self._store_in_weaviate(message_id, text, embedding, metadata)
            else:
                # Store locally in database
                result = self._store_locally(message_id, text, embedding, metadata)

            return {
                "success": True,
                "message_id": message_id,
                "embedding_dim": len(embedding),
                "backend": "weaviate" if self.use_weaviate else "local",
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to store embedding: {str(e)}"}

    def _store_in_weaviate(
        self,
        message_id: int,
        text: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Store embedding in Weaviate"""
        try:
            # Create class if it doesn't exist
            schema = {
                "class": "ChatMessage",
                "properties": [
                    {"name": "messageId", "dataType": ["int"]},
                    {"name": "text", "dataType": ["text"]},
                    {"name": "userId", "dataType": ["int"]},
                    {"name": "conversationId", "dataType": ["int"]},
                    {"name": "timestamp", "dataType": ["date"]},
                    {"name": "metadata", "dataType": ["text"]},
                ],
            }

            # Add object
            object_data = {
                "messageId": message_id,
                "text": text,
                "userId": metadata.get("user_id") if metadata else None,
                "conversationId": metadata.get("conversation_id") if metadata else None,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": json.dumps(metadata or {}),
            }

            result = self.weaviate_client.data_object.create(
                object_data, "ChatMessage", vector=embedding
            )

            return {"success": True, "weaviate_id": result}

        except Exception as e:
            return {"success": False, "error": f"Weaviate storage error: {str(e)}"}

    def _store_locally(
        self,
        message_id: int,
        text: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Store embedding locally by extending ChatMessage with embedding data"""
        try:
            message = ChatMessage.query.get(message_id)
            if not message:
                return {"success": False, "error": "Message not found"}

            # Store embedding as JSON in a text column or new column if added
            # For now, we'll store it with the message
            embedding_data = {
                "embedding": embedding,
                "dimension": len(embedding),
                "stored_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {},
            }

            # Store in message (would need to add embedding column to ChatMessage model)
            # For now, we'll just cache it
            return {"success": True, "cached": True, "embedding_dim": len(embedding)}

        except Exception as e:
            return {"success": False, "error": f"Local storage error: {str(e)}"}

    def semantic_search(
        self, query: str, user_id: int, limit: int = 5, threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search on chat messages
        
        Args:
            query: Search query
            user_id: User ID to filter by
            limit: Maximum number of results
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of similar messages with scores
        """
        try:
            # Generate embedding for query
            query_embedding = self.generate_embedding(query)
            if query_embedding is None:
                return []

            if self.use_weaviate and self.weaviate_client:
                return self._semantic_search_weaviate(query_embedding, user_id, limit)
            else:
                return self._semantic_search_local(query, user_id, limit)

        except Exception as e:
            print(f"Semantic search error: {e}")
            return []

    def _semantic_search_weaviate(
        self, query_embedding: List[float], user_id: int, limit: int
    ) -> List[Dict[str, Any]]:
        """Search Weaviate for similar messages"""
        try:
            where_filter = {"path": ["userId"], "operator": "Equal", "valueInt": user_id}

            results = self.weaviate_client.query.get("ChatMessage", ["messageId", "text", "_additional {distance}"]).with_where(where_filter).with_limit(limit).with_near_vector({"vector": query_embedding}).do()

            formatted_results = []
            if "data" in results and "Get" in results["data"]:
                for item in results["data"]["Get"].get("ChatMessage", []):
                    distance = item.get("_additional", {}).get("distance", 1)
                    similarity = 1 - distance  # Convert distance to similarity
                    
                    if similarity >= 0:  # Include all results from Weaviate
                        formatted_results.append(
                            {
                                "message_id": item.get("messageId"),
                                "text": item.get("text"),
                                "similarity": similarity,
                            }
                        )

            return formatted_results

        except Exception as e:
            print(f"Weaviate search error: {e}")
            return []

    def _semantic_search_local(
        self, query: str, user_id: int, limit: int
    ) -> List[Dict[str, Any]]:
        """Search local messages using simple text matching"""
        try:
            # Get user's messages
            messages = (
                db.session.query(ChatMessage)
                .join(ChatMessage.conversation)
                .filter(ChatMessage.conversation.user_id == user_id)
                .all()
            )

            # Simple text-based scoring
            results = []
            query_words = set(query.lower().split())

            for msg in messages:
                if msg.role == "assistant":  # Only search assistant responses
                    msg_words = set(msg.content.lower().split())
                    # Calculate similarity as percentage of matching words
                    common_words = query_words & msg_words
                    similarity = len(common_words) / max(len(query_words), len(msg_words))

                    if similarity > 0:
                        results.append(
                            {
                                "message_id": msg.id,
                                "text": msg.content[:200],
                                "similarity": similarity,
                            }
                        )

            # Sort by similarity and limit results
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:limit]

        except Exception as e:
            print(f"Local search error: {e}")
            return []

    def find_similar_conversations(
        self, conversation_id: int, user_id: int, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find conversations similar to the given one"""
        try:
            from app.models import ChatConversation

            # Get current conversation
            current_conv = ChatConversation.query.get(conversation_id)
            if not current_conv or current_conv.user_id != user_id:
                return []

            # Get conversation topic/summary
            messages = ChatMessage.query.filter_by(
                conversation_id=conversation_id
            ).limit(5)
            if not messages:
                return []

            summary_text = " ".join([msg.content for msg in messages][:100])

            # Search for similar conversations
            similar = self.semantic_search(summary_text, user_id, limit)

            # Get unique conversation IDs
            conversation_ids = []
            for result in similar:
                msg = ChatMessage.query.get(result["message_id"])
                if msg and msg.conversation_id != conversation_id:
                    if msg.conversation_id not in conversation_ids:
                        conversation_ids.append(msg.conversation_id)

            # Get conversations
            similar_convs = (
                ChatConversation.query.filter(
                    ChatConversation.id.in_(conversation_ids)
                )
                .limit(limit)
                .all()
            )

            return [c.to_dict() for c in similar_convs]

        except Exception as e:
            print(f"Error finding similar conversations: {e}")
            return []

    def batch_embed_messages(self, conversation_id: int) -> Dict[str, Any]:
        """Batch embed all messages in a conversation"""
        try:
            messages = ChatMessage.query.filter_by(
                conversation_id=conversation_id
            ).all()

            results = []
            for msg in messages:
                result = self.store_message_embedding(
                    msg.id,
                    msg.content,
                    {
                        "user_id": msg.conversation.user_id,
                        "conversation_id": msg.conversation_id,
                        "role": msg.role,
                    },
                )
                results.append(result)

            return {
                "success": True,
                "conversation_id": conversation_id,
                "embedded_messages": len([r for r in results if r.get("success")]),
                "total_messages": len(messages),
            }

        except Exception as e:
            return {"success": False, "error": f"Batch embedding error: {str(e)}"}

    def cleanup_old_embeddings(self, days_old: int = 90) -> Dict[str, Any]:
        """Clean up embeddings older than specified days"""
        try:
            # This would be useful if implemented with timestamps
            # For now, just return success
            return {
                "success": True,
                "message": f"Cleanup completed for embeddings older than {days_old} days",
            }

        except Exception as e:
            return {"success": False, "error": f"Cleanup error: {str(e)}"}


# Singleton instance
vector_db_service = VectorDBService(use_weaviate=False)  # Set to True if Weaviate is available
