import os
from mem0 import Memory

# # Set environment variables
os.environ["GOOGLE_API_KEY"] = "AIzaSyD3b5kg3ClLw7XLyO0li3_efk0t5-2k9j8"

config = {
    # Vector Store - Weaviate
    "vector_store": {
        "provider": "weaviate",
        "config": {
            "collection_name": "convai",
            "cluster_url": "z1w4coury6f0vbogfyw.c0.asia-southeast1.gcp.weaviate.cloud",  # Your Weaviate instance URL
            "auth_client_secret": "VEdWRVZGOVZrTzNMaWNqUF9WbzhudENSNExUaC9sdEk4ZTZRSTFhZzNBTlQwMEkxTk5FZEVMVGVtdDk4PV92MjAw",  # Add if using Weaviate Cloud
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