import os
from dotenv import load_dotenv
from mem0 import Memory

# # Set environment variables
load_dotenv()

config = {
    # Vector Store - Weaviate
    "vector_store": {
        "provider": "weaviate",
        "config": {
            "collection_name": "convai",
            "cluster_url": os.getenv("CLUSTER_URL"),
            "auth_client_secret": os.getenv("AUTH_CLIENT_SECRET"),
            "embedding_model_dims": 1536,  # Google AI embedding dimensions
        }
    },
    
    # LLM - Google AI (Gemini)
    "llm": {
        "provider": "gemini",
        "config": {
            "model": "gemini-2.5-flash",
            "temperature": 0.1,
            "max_tokens": 2000,
        }
    },
    
    # Embedder - Google AI
    "embedder": {
        "provider": "gemini",
        "config": {
            "model": "models/text-embedding-004",
            "embedding_dims": 1536,
        }
    },
  
    # Version and customization
    "version": "v1.1",
    "custom_fact_extraction_prompt": "Extract key facts and preferences from the conversation",
}

# Initialize Memory
memory_agent = Memory.from_config(config)