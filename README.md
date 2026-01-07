# Winter Assistant - Modular AI Chat System

Clean, modular architecture with swappable components and graceful fallbacks.

## 🏗️ Architecture
```
winter-assistant/
├── core/          # AI engine, interfaces, config
├── storage/       # LanceDB + JSONL fallback
├── retrieval/     # RAG strategies (hybrid/simple)
├── ui/            # Terminal interface
├── adapters/      # Orchestration layer
├── utils/         # Pure utility functions
└── main.py        # Entry point
```

## 🚀 Quick Start
```bash
# 1. Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Run
python main.py
```

## 🎯 Features

- ✅ **RAG-based memory** - Hybrid retrieval (recency + semantic)
- ✅ **Vector storage** - LanceDB with embeddings
- ✅ **Graceful fallbacks** - JSONL if LanceDB fails
- ✅ **Modular design** - Swap any component
- ✅ **Error boundaries** - No cascading failures
- ✅ **Zero coupling** - Clean interfaces between modules

## 🔧 Configuration

Copy `.env.example` to `.env` and customize:
```bash
WINTER_STORAGE=lancedb        # or jsonl
WINTER_AI_MODEL=deepseek-r1:8b
WINTER_RAG=hybrid             # or simple
```

## 📝 Commands

- `history` - Show recent conversation
- `search <query>` - Semantic search
- `quit` - Exit

## 🏛️ Design Principles

1. **Each module = one job** - Single responsibility
2. **Interfaces over implementations** - Swappable components
3. **Fail gracefully** - Error boundaries prevent cascades
4. **Explicit over implicit** - No magic, clear flow
5. **Zero cross-coupling** - Modules don't import each other

## 📦 Module Responsibilities

### `core/`
- `interfaces.py` - Abstract contracts (Storage, RAG, AI)
- `ai_engine.py` - AI inference (Ollama)
- `config.py` - Configuration management
- `errors.py` - Custom exceptions

### `storage/`
- `base.py` - Base storage class
- `lancedb_storage.py` - Vector storage implementation
- `fallback_storage.py` - Simple JSONL fallback

### `retrieval/`
- `hybrid_rag.py` - Recency + semantic search
- `simple_rag.py` - Recency-only fallback

### `ui/`
- `terminal.py` - Terminal interface
- `components.py` - Reusable UI elements

### `adapters/`
- `conversation_adapter.py` - Orchestrates core + storage + RAG

### `utils/`
- `file_ops.py` - File operations

## 🧪 Testing Fallbacks

**Disable LanceDB:**
```bash
# System gracefully falls back to JSONL storage
python main.py
```

**Disable embeddings:**
```bash
# System gracefully falls back to simple RAG
python main.py
```

## 🗂️ Legacy Code

Old JSONL + Redis sculpting system archived in `archive/legacy/`

## 📄 License

MIT
