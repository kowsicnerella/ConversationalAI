"""
Weaviate Memory Service (LangChain-based)
Manages user memories in Weaviate via LangChain's WeaviateVectorStore.

Replaces: app/services/mem0_service.py and app/services/vector_db_service.py
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)


class WeaviateMemoryService:
    """
    Manages user memories in Weaviate via LangChain's WeaviateVectorStore.

    Each memory is a LangChain Document with:
        page_content: The memory text
        metadata: {user_id, memory_type, conversation_id, timestamp, ...}

    User scoping: All queries filter by metadata.user_id.
    """

    def __init__(self):
        self._client = None
        self._vector_store = None
        self._embeddings: Optional[Embeddings] = None
        self._collection_name: str = "convai_langchain"
        self._initialized: bool = False

    def initialize(
        self,
        cluster_url: str,
        api_key: str,
        collection_name: str,
        embeddings: Embeddings,
        text_key: str = "content",
    ) -> None:
        """
        Initialize Weaviate client and LangChain vector store.
        Called once during Flask app startup.

        Args:
            cluster_url: Weaviate Cloud cluster URL
            api_key: Weaviate API key
            collection_name: Name for the Weaviate collection
            embeddings: LangChain Embeddings instance from LangChainConfig
            text_key: Property name for document text in Weaviate
        """
        if self._initialized:
            return

        self._embeddings = embeddings
        self._collection_name = collection_name

        try:
            import weaviate
            from weaviate.classes.init import Auth

            # Strip protocol if present in cluster_url
            url = cluster_url
            if not url.startswith("http"):
                url = f"https://{url}"

            self._client = weaviate.connect_to_weaviate_cloud(
                cluster_url=url,
                auth_credentials=Auth.api_key(api_key),
            )

            self._ensure_collection_exists(collection_name)

            from langchain_weaviate import WeaviateVectorStore

            self._vector_store = WeaviateVectorStore(
                client=self._client,
                index_name=collection_name,
                text_key=text_key,
                embedding=embeddings,
            )

            self._initialized = True
            logger.info(
                f"WeaviateMemoryService initialized: collection='{collection_name}'"
            )

        except Exception as e:
            logger.warning(f"WeaviateMemoryService initialization failed: {e}")
            self._client = None
            self._vector_store = None
            self._initialized = True  # Mark as initialized to prevent retries

    def _ensure_collection_exists(self, collection_name: str) -> None:
        """Create the Weaviate collection with proper schema if it doesn't exist."""
        if self._client.collections.exists(collection_name):
            logger.info(f"Collection '{collection_name}' already exists")
            return

        from weaviate.classes.config import Configure, Property, DataType

        self._client.collections.create(
            name=collection_name,
            vectorizer_config=Configure.Vectorizer.none(),
            properties=[
                Property(name="content", data_type=DataType.TEXT),
                Property(name="user_id", data_type=DataType.TEXT),
                Property(name="memory_type", data_type=DataType.TEXT),
                Property(name="conversation_id", data_type=DataType.TEXT),
                Property(name="timestamp", data_type=DataType.TEXT),
            ],
        )
        logger.info(f"Created Weaviate collection '{collection_name}' with schema")

    @property
    def is_available(self) -> bool:
        """Check if Weaviate connection is active."""
        return self._vector_store is not None and self._client is not None

    def close(self) -> None:
        """Close the Weaviate client connection."""
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass

    # ─── Core Memory Operations ───

    def add_memory(
        self,
        user_id: int,
        content: str,
        memory_type: str = "interaction",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Add a memory document for a user.

        Args:
            user_id: User ID
            content: Memory text content
            memory_type: Category (interaction, achievement, mistake, vocabulary, preference)
            metadata: Additional metadata

        Returns:
            {"success": bool, "document_id": str}
        """
        if not self.is_available:
            return {"success": False, "error": "Weaviate not available"}

        try:
            doc_metadata = {
                "user_id": str(user_id),
                "memory_type": memory_type,
                "timestamp": datetime.utcnow().isoformat(),
                **(metadata or {}),
            }

            # Ensure all metadata values are strings (Weaviate compatibility)
            clean_metadata = {}
            for k, v in doc_metadata.items():
                if v is not None:
                    clean_metadata[k] = str(v) if not isinstance(v, str) else v

            doc = Document(page_content=content, metadata=clean_metadata)
            ids = self._vector_store.add_documents([doc])

            return {
                "success": True,
                "document_id": ids[0] if ids else None,
                "message": "Memory saved",
            }

        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            return {"success": False, "error": str(e)}

    def search_memories(
        self,
        user_id: int,
        query: str,
        limit: int = 5,
        memory_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search across user's memories.

        Args:
            user_id: User ID
            query: Search query text
            limit: Max results
            memory_type: Optional filter by memory type

        Returns:
            List of memory dicts with content, metadata, and score
        """
        if not self.is_available:
            return []

        try:
            # Build Weaviate filter for user_id scoping
            from weaviate.classes.query import Filter

            filters = Filter.by_property("user_id").equal(str(user_id))
            if memory_type:
                filters = filters & Filter.by_property("memory_type").equal(memory_type)

            results = self._vector_store.similarity_search_with_score(
                query=query,
                k=limit,
                filters=filters,
            )

            memories = []
            for doc, score in results:
                memories.append({
                    "content": doc.page_content,
                    "memory": doc.page_content,  # Backward compat with mem0 format
                    "metadata": doc.metadata,
                    "score": score,
                    "memory_type": doc.metadata.get("memory_type", "interaction"),
                    "timestamp": doc.metadata.get("timestamp", ""),
                })

            return memories

        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            return []

    def get_user_memories(
        self,
        user_id: int,
        limit: int = 10,
        memory_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent memories for a user (uses a broad query for retrieval).

        Args:
            user_id: User ID
            limit: Max results
            memory_type: Optional filter by memory type

        Returns:
            List of memory dicts
        """
        if not self.is_available:
            return []

        try:
            # Use a generic query to retrieve recent memories
            return self.search_memories(
                user_id=user_id,
                query="recent learning interactions and activities",
                limit=limit,
                memory_type=memory_type,
            )
        except Exception as e:
            logger.error(f"Failed to get user memories: {e}")
            return []

    def delete_memory(self, document_id: str, user_id: int) -> Dict[str, Any]:
        """
        Delete a specific memory document.

        Args:
            document_id: Weaviate document UUID
            user_id: User ID (for authorization check)

        Returns:
            {"success": bool, "message": str}
        """
        if not self.is_available:
            return {"success": False, "error": "Weaviate not available"}

        try:
            self._vector_store.delete([document_id])
            return {"success": True, "message": "Memory deleted"}
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
            return {"success": False, "error": str(e)}

    def delete_all_user_memories(self, user_id: int) -> Dict[str, Any]:
        """
        Delete all memories for a user.

        Args:
            user_id: User ID

        Returns:
            {"success": bool, "deleted_count": int}
        """
        if not self.is_available:
            return {"success": False, "error": "Weaviate not available"}

        try:
            from weaviate.classes.query import Filter

            # Get all user's documents first
            collection = self._client.collections.get(self._collection_name)
            response = collection.query.fetch_objects(
                filters=Filter.by_property("user_id").equal(str(user_id)),
                limit=1000,
            )

            if response.objects:
                ids_to_delete = [obj.uuid for obj in response.objects]
                self._vector_store.delete(ids_to_delete)
                return {"success": True, "deleted_count": len(ids_to_delete)}

            return {"success": True, "deleted_count": 0}

        except Exception as e:
            logger.error(f"Failed to delete all user memories: {e}")
            return {"success": False, "error": str(e)}

    # ─── Composite Context Methods ───

    def get_conversation_context(
        self,
        user_id: int,
        query: str,
        limit: int = 5,
    ) -> Dict[str, Any]:
        """
        Get comprehensive context for a conversation turn.

        Returns dict with:
            relevant_memories: Semantic search results for the current query
            recent_memories: Last N memories regardless of relevance
            mistake_patterns: Memories of type 'mistake'
            vocabulary: Memories of type 'vocabulary'
        """
        if not self.is_available:
            return {
                "relevant_memories": [],
                "recent_memories": [],
                "mistake_patterns": [],
                "vocabulary": [],
            }

        try:
            relevant = self.search_memories(user_id, query, limit=limit)
            recent = self.get_user_memories(user_id, limit=5)
            mistakes = self.search_memories(
                user_id, "mistakes errors corrections", limit=3, memory_type="mistake"
            )
            vocabulary = self.search_memories(
                user_id, "vocabulary words learned", limit=3, memory_type="vocabulary"
            )

            return {
                "relevant_memories": relevant,
                "recent_memories": recent,
                "mistake_patterns": mistakes,
                "vocabulary": vocabulary,
            }

        except Exception as e:
            logger.error(f"Failed to get conversation context: {e}")
            return {
                "relevant_memories": [],
                "recent_memories": [],
                "mistake_patterns": [],
                "vocabulary": [],
            }

    # ─── Specialized Memory Storage ───

    def save_mistake_pattern(
        self, user_id: int, mistake_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save a mistake pattern for future reference."""
        content = (
            f"User made a {mistake_data.get('mistake_type', 'grammar')} mistake: "
            f"{mistake_data.get('original_text', '')}. "
            f"Correct form: {mistake_data.get('corrected_text', '')}. "
            f"{mistake_data.get('explanation', '')}"
        )
        return self.add_memory(
            user_id, content, memory_type="mistake", metadata=mistake_data
        )

    def save_vocabulary(
        self, user_id: int, vocab_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save vocabulary learning to memory."""
        content = (
            f"Learned '{vocab_data.get('english_word', '')}' "
            f"meaning '{vocab_data.get('telugu_translation', '')}' "
            f"in context: {vocab_data.get('context_sentence', '')}"
        )
        return self.add_memory(
            user_id, content, memory_type="vocabulary", metadata=vocab_data
        )

    def save_preference(
        self, user_id: int, pref_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save user learning preference."""
        content = f"User preference: {', '.join(f'{k}={v}' for k, v in pref_data.items())}"
        return self.add_memory(
            user_id, content, memory_type="preference", metadata=pref_data
        )

    def save_achievement(
        self, user_id: int, achievement_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save a learning achievement to memory."""
        content = (
            f"User achieved: {achievement_data.get('description', 'New achievement')}. "
            f"Type: {achievement_data.get('type', 'general')}. "
            f"Points: {achievement_data.get('points', 0)}"
        )
        return self.add_memory(
            user_id, content, memory_type="achievement", metadata=achievement_data
        )

    def get_personalized_suggestions(
        self, user_id: int, current_proficiency: str = "beginner"
    ) -> Dict[str, Any]:
        """
        Get personalized learning suggestions based on user's memory.
        Replaces: Mem0Service.get_personalized_suggestions()
        """
        try:
            weaknesses = self.search_memories(
                user_id, "mistakes weaknesses struggles difficult", limit=5
            )
            strengths = self.search_memories(
                user_id, "achievements strengths good performance", limit=3
            )
            interests = self.search_memories(
                user_id, "interests topics preferences likes", limit=3
            )

            return {
                "weaknesses": weaknesses,
                "strengths": strengths,
                "interests": interests,
                "proficiency_level": current_proficiency,
                "generated_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get suggestions: {e}")
            return {
                "weaknesses": [],
                "strengths": [],
                "interests": [],
                "error": str(e),
            }


# Singleton instance
weaviate_memory_service = WeaviateMemoryService()
