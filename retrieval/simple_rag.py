"""Simple RAG: Just recent context (fallback)"""
from typing import List, Dict, Any

from retrieval.base import BaseRAG
from core.interfaces import StorageInterface

class SimpleRAG(BaseRAG):
    """Simple recency-based retrieval"""
    
    def retrieve(self, query: str, storage: StorageInterface, limit: int) -> List[Dict[str, Any]]:
        """Just get recent turns - no semantic search needed"""
        return storage.get_recent(limit)
