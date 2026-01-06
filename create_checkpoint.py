import redis
import subprocess
import json
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Get current project
project = r.get("current_project")
if not project:
    print("No active project!")
    exit(1)

print(f"\n🍄 Creating checkpoint for: {project}\n")

# Get all project memory
facts = []
states = []
outcomes = []

pattern = f"project:{project}:*"
for key in r.keys(pattern):
    value = r.get(key)
    parts = key.split(':')
    if len(parts) >= 3:
        category = parts[2]
        key_name = ':'.join(parts[3:])
        
        if category == 'facts':
            facts.append(f"{key_name}: {value}")
        elif category == 'state':
            states.append(f"{key_name}: {value}")
        elif category == 'outcomes':
            outcomes.append(value)

# Ask LLM to compress everything
prompt = f"""Compress this project memory into ONE ultra-compact checkpoint summary.

PROJECT: {project}

FACTS: {json.dumps(facts[:10])}
STATES: {json.dumps(states[:10])}  
OUTCOMES: {json.dumps(outcomes[:10])}

Create a single paragraph (max 100 words) that captures:
- Core problem being solved
- Key findings/insights
- Current approach/solution

Be extremely concise. No fluff. Just the essence.

Checkpoint:"""

print("🧠 Compressing memory...")

result = subprocess.run(
    ['ollama', 'run', 'deepseek-r1:8b', prompt],
    capture_output=True,
    text=True,
    timeout=30
)

checkpoint = result.stdout
if "...done thinking." in checkpoint:
    checkpoint = checkpoint.split("...done thinking.")[-1].strip()

# Save checkpoint
checkpoint_key = f"project:{project}:checkpoint:latest"
r.set(checkpoint_key, json.dumps({
    "timestamp": int(time.time()),
    "summary": checkpoint,
    "stats": {
        "facts": len(facts),
        "states": len(states),
        "outcomes": len(outcomes)
    }
}))

print("\n🍄 CHECKPOINT CREATED")
print("="*60)
print(checkpoint)
print("="*60)
print(f"\n📊 Compressed: {len(facts)} facts, {len(states)} states, {len(outcomes)} outcomes")
print(f"💾 Saved to: {checkpoint_key}\n")
