#!/usr/bin/env python
"""
Winter Assistant - Modular AI Chat System
Clean architecture: swappable components, graceful degradation
"""
import sys

from core.config import Config
from core.ai_engine import OllamaAI
from storage.lancedb_storage import LanceDBStorage
from storage.fallback_storage import JSONLStorage
from retrieval.hybrid_rag import HybridRAG
from retrieval.simple_rag import SimpleRAG
from adapters.conversation_adapter import ConversationAdapter
from ui.terminal import TerminalUI
from core.errors import StorageError

def main():
    """Main entry point with graceful fallbacks"""
    
    print("🚀 Winter Assistant - Modular Edition\n")
    
    # Load configuration
    config = Config.load()
    
    # Initialize storage (with fallback)
    print("📦 Initializing storage...")
    try:
        storage = LanceDBStorage(config)
        print("✅ LanceDB storage ready\n")
    except StorageError as e:
        print(f"⚠️  LanceDB failed: {e}")
        print("📦 Falling back to JSONL storage\n")
        storage = JSONLStorage(config)
    
    # Initialize RAG (with fallback)
    print("🔍 Initializing RAG...")
    try:
        rag = HybridRAG(config)
        print("✅ Hybrid RAG (recency + semantic) ready\n")
    except Exception as e:
        print(f"⚠️  Hybrid RAG failed: {e}")
        print("🔍 Falling back to simple RAG\n")
        rag = SimpleRAG(config)
    
    # Initialize AI
    print("🤖 Initializing AI...")
    try:
        ai = OllamaAI(config)
        print("✅ AI engine ready\n")
    except Exception as e:
        print(f"❌ AI initialization failed: {e}")
        print("Cannot continue without AI engine.")
        sys.exit(1)
    
    # Wire everything together
    adapter = ConversationAdapter(storage, rag, ai)
    ui = TerminalUI(adapter)
    
    # Run
    try:
        ui.run()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
