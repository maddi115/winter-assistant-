import redis
import json
import sys
from datetime import datetime

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
project = r.get("current_project") or "default"

def get_time(ts):
    return datetime.fromtimestamp(ts).strftime('%b %d, %Y at %I:%M %p PT')

print(f"\n{'='*60}")
print(f"📦 PROJECT: {project.upper()}")
print(f"{'='*60}")

# 🗿 FOUNDATION
f_data = r.get(f"project:{project}:foundation:core")
if f_data:
    print("\n🗿 SACRED FOUNDATION")
    print("─" * 60)
    for p in json.loads(f_data).get('principles', []):
        print(f"  • {p['content']}\n     🔒 {get_time(p['timestamp'])}")
else:
    print("\n🗿 SACRED FOUNDATION (Empty)")

# 🍄 CHECKPOINTS (Last 3)
keys = sorted(r.keys(f"project:{project}:checkpoint:*"), reverse=True)
print(f"\n🍄 CHECKPOINT SUMMARIES (Last {min(3, len(keys))})")
print("─" * 60)
for k in keys[:3]:
    try:
        cp = json.loads(r.get(k))
        print(f"  - {cp['summary']}\n     📅 {get_time(cp['timestamp'])}")
    except:
        continue

if len(keys) > 3:
    print(f"\n  ... and {len(keys)-3} more. Type 'checkpoint list' to see all.")

print(f"\n{'='*60}\n")
