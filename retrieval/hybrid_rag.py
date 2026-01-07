"""Hybrid RAG: Recency + Semantic search"""
from typing import List, Dict, Any

from retrieval.base import BaseRAG
from core.interfaces import StorageInterface
from core.errors import RAGError

class HybridRAG(BaseRAG):
    """Combines recent context with semantic search"""
    
    def retrieve(self, query: str, storage: StorageInterface, limit: int) -> List[Dict[str, Any]]:
        """Hybrid retrieval: recent + relevant"""
        try:
            # Get recent turns
            recent = storage.get_recent(self.config.rag_recent_limit)
            
            # Get semantically relevant turns
            try:
                relevant = storage.search(query, self.config.rag_semantic_limit)
            except:
                # If semantic search fails, just use recent
                return recent
            
            # Deduplicate by turn_number + timestamp
            seen = set()
            combined = []
            
            for turn in recent:
                key = f"{turn.get('timestamp', 0)}_{turn.get('turn_number', 0)}"
                if key not in seen:
                    seen.add(key)
                    combined.append(turn)
            
            for turn in relevant:
                key = f"{turn.get('timestamp', 0)}_{turn.get('turn_number', 0)}"
                if key not in seen:
                    seen.add(key)
                    combined.append(turn)
            
            # Sort by timestamp
            combined.sort(key=lambda x: x.get('timestamp', 0))
            
            return combined[-limit:] if combined else []
            
        except Exception as e:
            raise RAGError(f"Hybrid RAG failed: {e}")
