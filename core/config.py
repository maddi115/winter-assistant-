"""Configuration management - all settings in one place"""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    # Storage
    storage_backend: str = "lancedb"
    storage_path: str = "./lance_db"
    
    # AI
    ai_model: str = "deepseek-r1:8b"
    ai_backend: str = "ollama"
    
    # RAG
    rag_strategy: str = "hybrid"
    rag_recent_limit: int = 3
    rag_semantic_limit: int = 3
    
    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Redis (legacy support)
    redis_host: str = "localhost"
    redis_port: int = 6379
    
    # UI
    ui_backend: str = "terminal"
    
    @classmethod
    def load(cls) -> 'Config':
        """Load configuration from environment or defaults"""
        return cls(
            storage_backend=os.getenv('WINTER_STORAGE', 'lancedb'),
            storage_path=os.getenv('WINTER_STORAGE_PATH', './lance_db'),
            ai_model=os.getenv('WINTER_AI_MODEL', 'deepseek-r1:8b'),
            rag_strategy=os.getenv('WINTER_RAG', 'hybrid'),
        )
