"""Base RAG retrieval"""
from core.interfaces import RAGInterface

class BaseRAG(RAGInterface):
    """Base RAG with common logic"""
    
    def __init__(self, config):
        self.config = config
