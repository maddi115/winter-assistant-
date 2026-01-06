# Winter Assistant ❄️

GPU-accelerated AI assistant with auto-curated project memories. Stores compressed semantic facts with weights—not conversations.

## Setup
```bash
cd ~/winter-assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage
```bash
ai              # Start assistant
memory          # View memory sculpture
checkpoint      # Create compressed summary
projects        # List all projects
```

## Requirements
- Python 3.12+
- Redis server running
- Ollama with deepseek-r1:8b model

## Memory Hierarchy
1. 🗿 Sacred Foundation (immutable core)
2. 🍄 Checkpoints (compressed summaries)
3. 📌 Facts (immutable)
4. 🔄 State (mutable with weights)
5. 💡 Outcomes (insights)
