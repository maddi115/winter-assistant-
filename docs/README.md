# ❄️ Winter Assistant

Local-first AI orchestrator powered by **Ollama (DeepSeek-R1)** and **LanceDB**. 

## 🚀 Status
- **RedisDB**: ~~SUNSETTED~~ (Removed)
- **Memory Sculpting**: ~~SUNSETTED~~ (Removed for speed/latency)
- **Primary Engine**: LanceDB Vector RAG

## 🛠 Execution
1. **Model**: `ollama pull deepseek-r1:8b`
2. **Launch**: `python lancedb_assistant.py`

## 🧠 Simplified Logic
The assistant now relies purely on **Semantic RAG**. It no longer attempts to "sculpt" or extract facts into secondary tables. Instead, it searches your conversation history in real-time to find relevant context.

## 🛠 In-Chat Commands
- `history`: Display last 10 session turns.
- `search <query>`: Semantic search across conversation history.
- `checkpoint`: Snapshot the current project state.

## 📂 Features
- **Multi-File Selection**: Ingest codebases for direct analysis.
- **Offline Geocoding**: Coordinate detection via `reverse_geocoder`.
