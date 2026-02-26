# Migration Documentation: Mem0 → LangChain/LangGraph + Weaviate

**Migration Date:** February 17, 2026
**Project:** Telugu-English Language Learning Platform
**Objective:** Replace mem0 with LangChain/LangGraph + Weaviate for chat/memory management

---

## Executive Summary

Successfully migrated from mem0-based chat architecture to a LangChain/LangGraph-based system with:
- **3 chat services → 1** consolidated LangGraph state machine
- **mem0 + vector_db → WeaviateMemoryService** with LangChain integration
- **Pluggable LLM config** via YAML (support custom endpoints, Gemini, OpenAI)
- **Fresh Weaviate collection** (`convai_langchain`) - no data migration
- **Zero downtime** - all old routes continue working in parallel

---

## Table of Contents

1. [Architecture Changes](#architecture-changes)
2. [Files Created](#files-created)
3. [Files Modified](#files-modified)
4. [API Changes](#api-changes)
5. [Implementation Phases](#implementation-phases)
6. [Deployment Guide](#deployment-guide)
7. [Testing Checklist](#testing-checklist)
8. [Rollback Plan](#rollback-plan)

---

## Architecture Changes

### Before: Fragmented Chat Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  4 Overlapping Route Blueprints                             │
├─────────────────────────────────────────────────────────────┤
│  /api/chat              → LearningSession + mem0 (oldest)   │
│  /api/chat-tutor        → ChatService (basic)               │
│  /api/enhanced-chat     → EnhancedChatService (mem0)        │
│  /api/chat-v2           → EnhancedChatServiceV2 (most complete) │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3 Separate Chat Services                                   │
├─────────────────────────────────────────────────────────────┤
│  ChatService                  → Basic chat                  │
│  EnhancedChatService          → Mem0 + context + vocab      │
│  EnhancedChatServiceV2        → Web search + mem0 + topics  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Memory & Vector Layer                                      │
├─────────────────────────────────────────────────────────────┤
│  mem0_service.py      → mem0ai library → Weaviate "convai"  │
│  vector_db_service.py → sentence-transformers → in-memory   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  LLM Layer                                                  │
├─────────────────────────────────────────────────────────────┤
│  LLMConfig (static methods, manual try/except fallback)     │
│    → vLLM (custom endpoint)                                 │
│    → Gemini (fallback)                                      │
│    → OpenAI (optional)                                      │
└─────────────────────────────────────────────────────────────┘
```

### After: Unified LangGraph Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  New Unified Route: /api/v3/chat                            │
│  + 4 old routes (backward compatible, running in parallel)  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  LangGraphChatService (singleton)                           │
│  4-Node State Machine:                                      │
│    [retrieve_memory] → [web_search?] → [generate_response]  │
│                     → [store_memory] → END                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────┬──────────────────────────────────┐
│  WeaviateMemoryService   │  LangChainConfig                 │
│  (LangChain wrapper)     │  (YAML-driven providers)         │
├──────────────────────────┼──────────────────────────────────┤
│  langchain-weaviate      │  ChatOpenAI(base_url=vLLM)       │
│  → Weaviate v4 client    │    .with_fallbacks([             │
│  → Collection:           │      ChatGoogleGenerativeAI()    │
│    "convai_langchain"    │    ])                            │
│  → Google embeddings     │                                  │
│    (text-embedding-004)  │                                  │
└──────────────────────────┴──────────────────────────────────┘
```

---

## Files Created

### 1. `llm_providers.yaml` (Project Root)

**Purpose:** Single configuration file for all LLM/embedding providers

**Structure:**
```yaml
llm_providers:
  vllm_primary:
    type: openai_compatible
    base_url: ${VLLM_ENDPOINT}/v1    # Resolved from .env
    model: sarvamai/sarvam-m
    priority: 1                       # Tried first

  gemini_fallback:
    type: google_genai
    model: gemini-2.0-flash-exp
    api_key: ${GEMINI_API_KEY}
    priority: 2                       # Fallback

embedding_providers:
  google_embedding:
    type: google_genai
    model: models/text-embedding-004
    api_key: ${GEMINI_API_KEY}

weaviate:
  cluster_url: ${WEAVIATE_URL}
  api_key: ${WEAVIATE_API_KEY}
  collection_name: convai_langchain
  text_key: content
```

**Key Features:**
- `${ENV_VAR}` syntax for secrets
- `priority` field determines fallback order
- Add new providers without touching Python code

---

### 2. `app/services/langchain_config.py`

**Purpose:** LLM provider manager - loads YAML, creates LangChain objects

**Key Classes & Methods:**

```python
class LangChainConfig:
    @classmethod
    def initialize(cls, config_path: str = None) -> None:
        """Load YAML, resolve env vars, instantiate all providers"""

    @classmethod
    def get_llm(cls, provider_name: str = None) -> BaseChatModel:
        """Get a specific LLM or highest-priority one"""

    @classmethod
    def get_llm_with_fallback(cls) -> BaseChatModel:
        """Returns LLM with .with_fallbacks() chain configured"""

    @classmethod
    def get_embeddings(cls, provider_name: str = None) -> Embeddings:
        """Get embedding model instance"""

    @classmethod
    def get_weaviate_config(cls) -> Dict[str, str]:
        """Returns Weaviate connection details"""
```

**Comparison to Old `llm_config.py`:**

| Old `LLMConfig` | New `LangChainConfig` |
|---|---|
| `LLMConfig.chat_completion(messages, system_prompt)` → dict | `LangChainConfig.get_llm_with_fallback().invoke(messages)` → AIMessage |
| Manual try/except for fallback | LangChain's `with_fallbacks()` - automatic |
| Direct HTTP calls to APIs | Abstracted through LangChain providers |
| Hardcoded in Python | Config-driven via YAML |

**Note:** Old `llm_config.py` remains **untouched** - still used by activity generator, assessment service, etc.

---

### 3. `app/services/weaviate_memory_service.py`

**Purpose:** Replaces `mem0_service.py` + `vector_db_service.py`

**Architecture:**
```python
class WeaviateMemoryService:
    # Weaviate v4 client
    _client: weaviate.WeaviateClient

    # LangChain wrapper
    _vector_store: WeaviateVectorStore

    # Embeddings from LangChainConfig
    _embeddings: Embeddings
```

**Document Schema in Weaviate:**
```python
Document(
    page_content="User asked: How do I use past tense?",  # Vectorized
    metadata={
        "user_id": "1",              # Always present, used for filtering
        "memory_type": "interaction", # interaction|achievement|mistake|vocabulary|preference
        "conversation_id": "42",      # Optional
        "timestamp": "2026-02-17T...", # ISO format
        "topic": "grammar"            # Optional, type-specific
    }
)
```

**Method Mapping:**

| Old (Mem0Service) | New (WeaviateMemoryService) |
|---|---|
| `add_user_interaction(user_id, message, context, metadata)` | `add_memory(user_id, content, memory_type, metadata)` |
| `search_user_memories(query, user_id, limit)` | `search_memories(user_id, query, limit, memory_type?)` |
| `get_user_memories(user_id, limit)` | `get_user_memories(user_id, limit, memory_type?)` |
| `delete_user_memory(memory_id, user_id)` | `delete_memory(document_id, user_id)` |
| `get_user_context_for_conversation(user_id, conversation_type)` | `get_conversation_context(user_id, query, limit)` |
| `save_mistake_pattern(user_id, mistake_data)` | `save_mistake_pattern(user_id, mistake_data)` |
| `save_vocabulary_learning(user_id, vocabulary_data)` | `save_vocabulary(user_id, vocab_data)` |
| `save_user_preference(user_id, preference_data)` | `save_preference(user_id, pref_data)` |
| `save_learning_achievement(user_id, achievement_data)` | `save_achievement(user_id, achievement_data)` |

**Key Differences:**
- **User scoping:** All queries filter by `metadata.user_id` using Weaviate v4 filters
- **Fresh collection:** `convai_langchain` (old `convai` collection untouched)
- **Direct control:** You manage embeddings via `langchain_config.py`
- **LangChain integration:** Native `Document` objects, `similarity_search_with_score()`

---

### 4. `app/services/langgraph_chat_service.py`

**Purpose:** Consolidated chat service - replaces all 3 chat services

**LangGraph State Machine:**

```python
class ConversationState(TypedDict):
    # Input
    user_id: int
    conversation_id: int
    user_message: str
    topic: str                    # "general" | "grammar" | "vocabulary" | "conversation"
    use_web_search: bool

    # Populated by nodes
    user_context: Dict[str, Any]
    relevant_memories: List[Dict]
    web_results: List[Dict]
    ai_response_raw: str
    ai_response_parsed: Dict[str, Any]
    model_used: str
    tokens_used: int
    response_time: float
    memory_stored: bool
    success: bool
    error: Optional[str]
```

**Graph Flow:**

```
START
  ↓
┌─────────────────┐
│ retrieve_memory │  ← Node 1
├─────────────────┤
│ • Query Profile, ProficiencyAssessment, MistakePattern from PostgreSQL
│ • Semantic search in Weaviate for memories matching user message
│ • Output: user_context + relevant_memories
└────────┬────────┘
         │
    ┌────▼────┐
    │ Condition│
    │use_web_ │
    │search?  │
    └─┬────┬──┘
  Yes │    │ No
      │    └────────────────┐
┌─────▼─────┐               │
│web_search │  ← Node 2     │
├───────────┤               │
│ • DuckDuckGo search       │
│ • Output: web_results     │
└─────┬─────┘               │
      │                     │
      └──────────┬──────────┘
                 │
      ┌──────────▼──────────┐
      │ generate_response   │  ← Node 3
      ├─────────────────────┤
      │ • Build system prompt: topic + profile + memories + web results
      │ • Load last 10 messages from DB as history
      │ • Call LLM via LangChainConfig.get_llm_with_fallback()
      │ • Parse response: Telugu, grammar, examples, corrections, vocab
      │ • Output: ai_response_raw + ai_response_parsed + metadata
      └──────────┬──────────┘
                 │
      ┌──────────▼──────────┐
      │   store_memory      │  ← Node 4
      ├─────────────────────┤
      │ • Save user + assistant ChatMessages to PostgreSQL
      │ • Update ChatConversation.message_count
      │ • Store interaction summary in Weaviate
      │ • Extract and save VocabularyWord entries
      │ • Output: success=True
      └──────────┬──────────┘
                 │
                END
```

**System Prompts by Topic:**

```python
SYSTEM_PROMPTS = {
    "general": """Expert tutor for Telugu speakers...""",
    "grammar": """Grammar expert focusing on...""",
    "vocabulary": """Vocabulary building expert...""",
    "conversation": """Conversational English expert...""",
}
```

**Logic Ported From:**

| Method | Source | Purpose |
|---|---|---|
| `_build_user_context()` | `EnhancedChatService` | Query Profile, Assessment, Mistakes from DB |
| `_build_system_prompt()` | Both Enhanced services | Merge topic prompt + learner profile + memories + web |
| `_parse_response()` | `EnhancedChatService._parse_enhanced_response()` | Extract Telugu, grammar, examples, corrections, vocab |
| `_extract_and_save_vocabulary()` | `EnhancedChatService` | Save VocabularyWord entries to PostgreSQL |
| Web search | `EnhancedChatServiceV2.search_web()` | DuckDuckGo integration |
| Learning insights | `EnhancedChatServiceV2` | Analytics across conversations |

**Public API Methods (backward compatible):**

```python
class LangGraphChatService:
    def send_message(conversation_id, user_message, user_id, use_web_search, topic)
    def create_conversation(user_id, title?, topic?)
    def get_conversation(conversation_id, user_id)
    def get_user_conversations(user_id, limit, offset)
    def delete_conversation(conversation_id, user_id)
    def update_conversation_title(conversation_id, user_id, title)
    def generate_summary(conversation_id, user_id)
    def get_learning_insights(user_id)
    def get_conversation_analytics(conversation_id, user_id)
    def search_user_memories(user_id, query, limit)
    def search_conversations(user_id, query, limit)
    def export_conversation(conversation_id, user_id, format)
```

---

### 5. `app/routes/unified_chat_routes.py`

**Purpose:** Consolidated chat API at `/api/v3/chat`

**Blueprint:** `unified_chat_bp`
**Auth:** All endpoints use `@jwt_required()` + `get_jwt_identity()`

**Endpoint Summary (17 total):**

| Method | Endpoint | Description |
|---|---|---|
| **Conversation CRUD** | | |
| `POST` | `/conversations` | Create conversation |
| `GET` | `/conversations` | List user conversations |
| `GET` | `/conversations/<id>` | Get conversation + messages |
| `DELETE` | `/conversations/<id>` | Soft-delete conversation |
| `PATCH` | `/conversations/<id>/title` | Update title |
| **Messaging** | | |
| `POST` | `/conversations/<id>/messages` | **Send message** (core) |
| `GET` | `/conversations/<id>/messages` | Get paginated messages |
| **Analytics** | | |
| `GET` | `/conversations/<id>/summary` | AI-generated summary |
| `GET` | `/conversations/<id>/analytics` | Conversation analytics |
| `GET` | `/conversations/<id>/export` | Export (json/markdown) |
| `GET` | `/insights` | Learning insights |
| `GET` | `/statistics` | Alias for insights |
| **Search & Memory** | | |
| `GET` | `/conversations/search` | Search conversations by topic |
| `POST` | `/memories/search` | Semantic memory search |
| `GET` | `/memories` | Get recent memories |
| `DELETE` | `/memories/<doc_id>` | Delete a memory |
| **Utilities** | | |
| `POST` | `/web-search` | Standalone DuckDuckGo search |
| `GET` | `/health` | Health check (no auth) |

---

## Files Modified

### 1. `requirements.txt`

**Added Dependencies:**
```txt
# LangChain / LangGraph
langchain>=0.3.0
langchain-core>=0.3.0
langchain-community>=0.3.0
langgraph>=0.2.0
langchain-openai>=0.2.0
langchain-google-genai>=2.0.0
langchain-weaviate>=0.1.0
weaviate-client>=4.9.0       # Upgrade from v0.1.2 to v4.9.0
pyyaml>=6.0
```

**Note:** `mem0ai` package remains (used by old routes) - can be removed after full migration.

---

### 2. `app/__init__.py`

**Change:** Added initialization block after blueprint registrations

```python
# ─── LangChain / LangGraph / Weaviate Initialization ───
try:
    from app.services.langchain_config import LangChainConfig
    LangChainConfig.initialize()

    from app.services.weaviate_memory_service import weaviate_memory_service
    weaviate_cfg = LangChainConfig.get_weaviate_config()
    if weaviate_cfg.get("cluster_url"):
        weaviate_memory_service.initialize(
            cluster_url=weaviate_cfg["cluster_url"],
            api_key=weaviate_cfg["api_key"],
            collection_name=weaviate_cfg["collection_name"],
            embeddings=LangChainConfig.get_embeddings(),
            text_key=weaviate_cfg.get("text_key", "content"),
        )

    from app.routes.unified_chat_routes import unified_chat_bp
    app.register_blueprint(unified_chat_bp, url_prefix="/api/v3/chat")
except Exception as e:
    import logging
    logging.getLogger(__name__).warning(f"LangChain/Weaviate init skipped: {e}")
```

**Effect:**
- On startup, loads LLM providers and connects to Weaviate
- Registers new `/api/v3/chat` blueprint
- Graceful degradation: if init fails, app still starts (old routes work)

---

### 3. `app/services/chat_history_service.py`

**Change:** Removed unused import

```diff
- from app.services.mem0_service import mem0_service
```

**Effect:** None - this import was never used in the file. Pure cleanup.

---

### 4. `app/services/personalization_service.py`

**Changes:**

1. **Import replacement (line 15):**
```diff
- from app.services.mem0_service import mem0_service
+ from app.services.weaviate_memory_service import weaviate_memory_service
```

2. **Method call update (lines 540-550):**
```diff
- mem0_service.save_vocabulary_learning(
-     user_id=user_id,
-     vocabulary_data={
-         "english_word": english_word,
-         "telugu_translation": telugu_translation,
-         "context_sentence": context_sentence,
-         "is_new_word": is_new_word,
-         "source": "personalization_tracking",
-     },
- )

+ if weaviate_memory_service.is_available:
+     weaviate_memory_service.save_vocabulary(
+         user_id=user_id,
+         vocab_data={
+             "english_word": english_word,
+             "telugu_translation": telugu_translation,
+             "context_sentence": context_sentence,
+             "is_new_word": str(is_new_word),  # Convert bool to string
+             "source": "personalization_tracking",
+         },
+     )
```

**Effect:** Vocabulary tracking now uses Weaviate instead of mem0, with graceful fallback if Weaviate unavailable.

---

## API Changes

### Core Endpoint: Send Message

#### Old Endpoints (3 separate, different features)

**1. Basic chat (no memory):**
```
POST /api/chat-tutor/conversations/<id>/messages
Body: { "message": "How do I use past tense?" }
```

**2. Mem0-powered (context + vocab):**
```
POST /api/enhanced-chat/conversations/<id>/send
Body: { "message": "How do I use past tense?" }
```

**3. Full-featured (mem0 + web search + topics):**
```
POST /api/chat-v2/conversations/<id>/messages
Body: {
  "message": "How do I use past tense?",
  "use_web_search": false,
  "topic": "grammar"
}
```

#### New Unified Endpoint (superset of all features)

```
POST /api/v3/chat/conversations/<id>/messages
Body: {
  "message": "How do I use past tense?",      // Required
  "use_web_search": false,                    // Optional, default: false
  "topic": "general"                          // Optional, default: "general"
                                              // Values: "general" | "grammar" | "vocabulary" | "conversation"
}
```

**Response Format:**
```json
{
  "success": true,
  "user_message": {
    "id": 101,
    "conversation_id": 42,
    "role": "user",
    "content": "How do I use past tense?",
    "created_at": "2026-02-17T10:30:00"
  },
  "ai_response": {
    "id": 102,
    "conversation_id": 42,
    "role": "assistant",
    "content": "Past tense is used to describe actions that happened in the past...",
    "telugu_translation": "(గతకాలం అంటే గడిచిపోయిన సమయంలో జరిగిన చర్యలను వివరించడానికి ఉపయోగిస్తారు)",
    "grammar_explanation": "Rule: Add -ed to regular verbs. For irregular verbs, the form changes...",
    "examples": "[\"I walked to school\", \"She played tennis\", \"We talked yesterday\"]",
    "correction": null,
    "tokens_used": 450,
    "model_used": "gemini-2.0-flash-exp",
    "response_time": 2.3,
    "created_at": "2026-02-17T10:30:02"
  },
  "conversation": {
    "id": 42,
    "user_id": 1,
    "title": "Learning Session - Feb 17, 10:30 AM",
    "topic": "General Learning",
    "message_count": 4,
    "is_active": true,
    "created_at": "2026-02-17T10:00:00",
    "updated_at": "2026-02-17T10:30:02"
  },
  "web_search_used": false,
  "web_results": [],
  "context_used": {
    "proficiency_level": "beginner",
    "memories_used": 3,
    "learning_style": "visual"
  },
  "response_time": 2.3
}
```

**Key Fields:**
- `telugu_translation`: Auto-extracted Telugu text from response
- `grammar_explanation`: Extracted grammar rules/explanations
- `examples`: Array of example sentences (parsed from response)
- `correction`: Any corrections made to user's message
- `web_results`: DuckDuckGo search results (if `use_web_search: true`)
- `context_used`: Summary of personalization context applied

---

### Conversation CRUD

| Old Endpoint | New Endpoint | Changes |
|---|---|---|
| `POST /api/chat-v2/conversations` | `POST /api/v3/chat/conversations` | User ID now from JWT (not body) |
| `GET /api/chat-v2/conversations` | `GET /api/v3/chat/conversations` | Same query params (`limit`, `offset`) |
| `GET /api/chat-v2/conversations/<id>` | `GET /api/v3/chat/conversations/<id>` | Same response shape |
| `DELETE /api/chat-v2/conversations/<id>` | `DELETE /api/v3/chat/conversations/<id>` | No body needed |
| *(didn't exist)* | `PATCH /api/v3/chat/conversations/<id>/title` | **NEW** - Update title |

---

### Analytics & Insights

| Old Endpoint | New Endpoint | Changes |
|---|---|---|
| `GET /api/chat-v2/conversations/<id>/analytics` | `GET /api/v3/chat/conversations/<id>/analytics` | Same response |
| `GET /api/chat-v2/conversations/<id>/summary` | `GET /api/v3/chat/conversations/<id>/summary` | Same response |
| `GET /api/chat-v2/insights` | `GET /api/v3/chat/insights` | Same response |
| *(didn't exist)* | `GET /api/v3/chat/statistics` | **NEW** - Alias for insights |
| *(didn't exist)* | `GET /api/v3/chat/conversations/<id>/export` | **NEW** - Export format: `json\|markdown` |

---

### Memory Management

| Old Endpoint | New Endpoint | Changes |
|---|---|---|
| `POST /api/chat-v2/memories/search` | `POST /api/v3/chat/memories/search` | Same body: `{query, limit?}` |
| `GET /api/chat-v2/memories` | `GET /api/v3/chat/memories` | Same query params |
| `DELETE /api/chat-v2/memories/<id>` | `DELETE /api/v3/chat/memories/<doc_id>` | **ID format changed:** mem0 ID → Weaviate UUID |

**Memory Response Format:**
```json
{
  "success": true,
  "memories": [
    {
      "content": "User asked: How do I introduce myself?",
      "memory": "User asked: How do I introduce myself?",  // Backward compat
      "metadata": {
        "user_id": "1",
        "memory_type": "interaction",
        "conversation_id": "38",
        "timestamp": "2026-02-16T14:20:00",
        "topic": "conversation"
      },
      "score": 0.87  // Relevance score from vector search
    }
  ],
  "count": 1
}
```

---

### New Endpoints (didn't exist before)

| Endpoint | Purpose | Request/Response |
|---|---|---|
| `GET /api/v3/chat/conversations/search?query=grammar` | Search conversations by topic | Returns matching conversations |
| `POST /api/v3/chat/web-search` | Standalone DuckDuckGo search | Body: `{query, max_results?}` |
| `GET /api/v3/chat/health` | Health check (**no auth**) | Shows LLM providers, Weaviate status |

**Health Check Response:**
```json
{
  "status": "healthy",
  "weaviate_available": true,
  "llm_providers": ["vllm_primary", "gemini_fallback"],
  "embedding_providers": ["google_embedding"]
}
```

---

## Implementation Phases

### Phase 1: Foundation (No Existing Code Touched)
✅ **Completed**

1. Created `llm_providers.yaml`
2. Created `app/services/langchain_config.py`
3. Added LangChain/LangGraph dependencies to `requirements.txt`

**Risk:** None - purely additive

---

### Phase 2: Weaviate Memory Service (No Existing Code Touched)
✅ **Completed**

4. Created `app/services/weaviate_memory_service.py`
5. Fresh Weaviate collection: `convai_langchain`

**Risk:** None - new collection, old `convai` collection untouched

---

### Phase 3: LangGraph Chat Service (No Existing Code Touched)
✅ **Completed**

6. Created `app/services/langgraph_chat_service.py`
7. Ported all logic from 3 chat services

**Risk:** None - new file, old services untouched

---

### Phase 4: Routes + App Integration (Additive Only)
✅ **Completed**

8. Created `app/routes/unified_chat_routes.py`
9. Updated `app/__init__.py` - added initialization + registered new blueprint

**Risk:** Low - new URL prefix `/api/v3/chat`, old routes continue working

---

### Phase 5: Cleanup (After Frontend Migration)
✅ **Completed** (Partial - proactive cleanup)

10. Removed unused mem0 import from `chat_history_service.py`
11. Updated `personalization_service.py` to use `weaviate_memory_service`

**Remaining (optional, do after frontend fully migrated):**
- Remove old route blueprints from `app/__init__.py`
- Delete deprecated service files
- Remove `mem0ai` from `requirements.txt`

---

## Deployment Guide

### Prerequisites

1. **Python 3.10+**
2. **Environment variables** in `.env`:
   ```env
   # Existing (unchanged)
   GEMINI_API_KEY=AIzaSy...
   WEAVIATE_URL=5anxxbbaq...
   WEAVIATE_API_KEY=S3hSUFYx...
   VLLM_ENDPOINT=https://..

   # New (optional - for future providers)
   # OPENAI_API_KEY=sk-...
   ```

---

### Step 1: Install Dependencies

```bash
cd language-learning-platform
pip install -r requirements.txt
```

**Expected new packages:**
- `langchain`, `langchain-core`, `langchain-community`
- `langgraph`
- `langchain-openai`, `langchain-google-genai`
- `langchain-weaviate`
- `weaviate-client` (v4.9.0+)
- `pyyaml`

---

### Step 2: Verify Configuration

Check that `llm_providers.yaml` exists in project root:
```bash
ls language-learning-platform/llm_providers.yaml
```

---

### Step 3: Start the Application

```bash
python app.py
# or
flask run
```

**Watch startup logs for:**
```
INFO - LLM provider 'vllm_primary' initialized (priority 1)
INFO - LLM provider 'gemini_fallback' initialized (priority 2)
INFO - Embedding provider 'google_embedding' initialized (priority 1)
INFO - LangChainConfig initialized: 2 LLM(s), 1 embedding(s)
INFO - WeaviateMemoryService initialized: collection='convai_langchain'
```

**If you see warnings:**
```
WARNING - LangChain/Weaviate init skipped: [error message]
```
→ App still starts, old routes work. Check `.env` and `llm_providers.yaml`

---

### Step 4: Health Check

```bash
curl http://localhost:5000/api/v3/chat/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "weaviate_available": true,
  "llm_providers": ["vllm_primary", "gemini_fallback"],
  "embedding_providers": ["google_embedding"]
}
```

---

### Step 5: Test New Endpoint

**Create a conversation:**
```bash
curl -X POST http://localhost:5000/api/v3/chat/conversations \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Conversation",
    "topic": "grammar"
  }'
```

**Send a message:**
```bash
curl -X POST http://localhost:5000/api/v3/chat/conversations/1/messages \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I use past tense?",
    "use_web_search": false,
    "topic": "grammar"
  }'
```

---

### Step 6: Monitor Logs

Watch for:
- **LLM fallback:** `INFO - Custom LLM failed: [error]. Falling back to Gemini...`
- **Weaviate writes:** `INFO - Memory saved` (from Weaviate)
- **Graph execution:** Each node logs its execution

---

## Testing Checklist

### Unit Tests

- [ ] `LangChainConfig.initialize()` loads YAML correctly
- [ ] `LangChainConfig.get_llm_with_fallback()` returns LLM with fallback chain
- [ ] Environment variable resolution (`${VAR}` → actual value)
- [ ] `WeaviateMemoryService.add_memory()` stores document in Weaviate
- [ ] `WeaviateMemoryService.search_memories()` filters by `user_id` correctly
- [ ] `WeaviateMemoryService.delete_memory()` removes document

### Integration Tests

- [ ] Create conversation → returns conversation object
- [ ] Send message without web search → AI responds
- [ ] Send message with `use_web_search: true` → includes DuckDuckGo results
- [ ] Send message with `topic: "grammar"` → uses grammar-specific prompt
- [ ] Memory search → returns user-scoped memories only
- [ ] LLM fallback → if vLLM fails, Gemini responds

### API Tests

- [ ] `POST /api/v3/chat/conversations` → 201
- [ ] `GET /api/v3/chat/conversations` → list of conversations
- [ ] `POST /api/v3/chat/conversations/<id>/messages` → AI response
- [ ] `GET /api/v3/chat/conversations/<id>/summary` → summary text
- [ ] `GET /api/v3/chat/insights` → learning insights
- [ ] `POST /api/v3/chat/memories/search` → memories list
- [ ] `GET /api/v3/chat/health` (no auth) → healthy status

### Regression Tests

- [ ] Old `/api/chat-tutor` endpoints still work
- [ ] Old `/api/enhanced-chat` endpoints still work
- [ ] Old `/api/chat-v2` endpoints still work
- [ ] Non-chat services (activity generator, assessment) work unchanged

### Performance Tests

- [ ] Response time comparable to old system (2-4 seconds)
- [ ] LLM fallback adds <1 second overhead
- [ ] Weaviate memory search <500ms

---

## Rollback Plan

### Emergency Rollback (if critical issue in production)

**Option 1: Disable new blueprint**

In `app/__init__.py`, comment out:
```python
# from app.routes.unified_chat_routes import unified_chat_bp
# app.register_blueprint(unified_chat_bp, url_prefix="/api/v3/chat")
```

Restart app. Old routes continue working.

---

**Option 2: Revert LangChain init**

In `app/__init__.py`, comment out entire LangChain block:
```python
# try:
#     from app.services.langchain_config import LangChainConfig
#     ...
# except Exception as e:
#     ...
```

Restart app. Zero impact on existing functionality.

---

**Option 3: Full rollback (Git)**

```bash
git log --oneline  # Find commit before migration
git revert <commit-hash>
git push
```

Redeploy. All old code restored.

---

### Partial Rollback (frontend not ready)

Keep new backend code deployed, but don't switch frontend to `/api/v3/chat`. Old routes continue working indefinitely.

---

## Data Migration (Future, Optional)

### Migrating Existing Memories from `convai` to `convai_langchain`

**Not implemented** - started fresh with `convai_langchain`.

If needed later:

```python
# Migration script (pseudocode)
from mem0 import Memory
from app.services.weaviate_memory_service import weaviate_memory_service

old_memory = Memory.from_config({...})  # Point to old collection

for user_id in get_all_user_ids():
    old_memories = old_memory.get_all(user_id=str(user_id))

    for mem in old_memories:
        weaviate_memory_service.add_memory(
            user_id=int(user_id),
            content=mem.get("memory", ""),
            memory_type="interaction",
            metadata=mem.get("metadata", {})
        )
```

**Estimated time:** 100 memories/second → ~1 hour for 100k memories.

---

## Known Limitations & Future Improvements

### Current Limitations

1. **No streaming:** LangGraph `.invoke()` is synchronous - consider `.astream()` for token streaming
2. **No conversation branching:** State machine is linear - no "undo" or branching paths
3. **Memory TTL:** No automatic memory expiration - consider adding `ttl` metadata
4. **Rate limiting:** No built-in rate limiting on new endpoints

### Future Improvements

1. **Add LangGraph checkpointing:**
   ```python
   from langgraph.checkpoint.sqlite import SqliteSaver
   checkpointer = SqliteSaver("checkpoints.db")
   graph.compile(checkpointer=checkpointer)
   ```
   → Enables conversation resume, state inspection

2. **Add more LLM providers:**
   Edit `llm_providers.yaml`:
   ```yaml
   anthropic_claude:
     type: anthropic
     model: claude-3-5-sonnet-20241022
     api_key: ${ANTHROPIC_API_KEY}
     priority: 3
   ```

3. **Add memory summarization:**
   Periodically summarize old memories to reduce vector DB size

4. **Add A/B testing:**
   Route percentage of traffic to `/api/v3/chat` vs old endpoints

5. **Migrate to async:**
   Convert Flask to FastAPI for native `async/await` support

---

## Support & Troubleshooting

### Common Issues

**Issue:** `ImportError: No module named 'langchain'`
**Fix:** `pip install -r requirements.txt`

---

**Issue:** `WeaviateMemoryService initialization failed: 401 Unauthorized`
**Fix:** Check `WEAVIATE_API_KEY` in `.env` - ensure no quotes in URL: `WEAVIATE_URL=cluster.weaviate.cloud` (not `"cluster.weaviate.cloud"`)

---

**Issue:** `LLM provider 'vllm_primary' not found`
**Fix:** Check `VLLM_ENDPOINT` in `.env` - if not set, only Gemini will be available

---

**Issue:** Old routes return `NameError: name 'mem0_service' is not defined`
**Fix:** `personalization_service.py` import was updated - ensure it has:
```python
from app.services.weaviate_memory_service import weaviate_memory_service
```

---

**Issue:** New endpoint returns 500: `'NoneType' object has no attribute 'to_dict'`
**Fix:** Conversation not found - ensure conversation belongs to user making request

---

### Debug Mode

Enable verbose LangChain logging:
```python
import logging
logging.getLogger("langchain").setLevel(logging.DEBUG)
logging.getLogger("langgraph").setLevel(logging.DEBUG)
```

---

## Appendix

### Full File Tree (New/Modified)

```
language-learning-platform/
├── llm_providers.yaml                          [NEW]
├── requirements.txt                            [MODIFIED]
├── app/
│   ├── __init__.py                             [MODIFIED]
│   ├── services/
│   │   ├── langchain_config.py                 [NEW]
│   │   ├── weaviate_memory_service.py          [NEW]
│   │   ├── langgraph_chat_service.py           [NEW]
│   │   ├── chat_history_service.py             [MODIFIED - cleanup]
│   │   ├── personalization_service.py          [MODIFIED - mem0→weaviate]
│   │   ├── chat_service.py                     [DEPRECATED - still works]
│   │   ├── enhanced_chat_service.py            [DEPRECATED - still works]
│   │   ├── enhanced_chat_service_v2.py         [DEPRECATED - still works]
│   │   ├── mem0_service.py                     [DEPRECATED - still used by old routes]
│   │   └── vector_db_service.py                [DEPRECATED - unused]
│   └── routes/
│       ├── unified_chat_routes.py              [NEW]
│       └── chat_routes.py                      [OLD - still registered]
└── migrations/                                  [No changes - DB schema unchanged]
```

### Dependencies Added

```
langchain>=0.3.0
langchain-core>=0.3.0
langchain-community>=0.3.0
langgraph>=0.2.0
langchain-openai>=0.2.0
langchain-google-genai>=2.0.0
langchain-weaviate>=0.1.0
weaviate-client>=4.9.0
pyyaml>=6.0
```

### Environment Variables Used

```env
# LLM Providers
GEMINI_API_KEY=AIzaSy...
VLLM_ENDPOINT=https://...
# OPENAI_API_KEY=sk-...  (optional)

# Weaviate
WEAVIATE_URL=cluster.weaviate.cloud
WEAVIATE_API_KEY=S3hSUFYx...

# Database (unchanged)
SUPABASE_DATABASE_URL=postgresql://...
```

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-02-17 | Initial migration complete |

---

**End of Migration Documentation**
