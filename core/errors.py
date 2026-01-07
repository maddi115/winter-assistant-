"""Custom exceptions for graceful error handling"""

class WinterError(Exception):
    """Base exception for Winter Assistant"""
    pass

class StorageError(WinterError):
    """Storage operation failed"""
    pass

class RAGError(WinterError):
    """RAG retrieval failed"""
    pass

class AIError(WinterError):
    """AI generation failed"""
    pass

class UIError(WinterError):
    """UI operation failed"""
    pass

class ConfigError(WinterError):
    """Configuration error"""
    pass
