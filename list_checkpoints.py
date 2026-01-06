import redis
import json
import sys
from datetime import datetime

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
project = r.get("current_project")

checkpoint_keys = sorted([k for k in r.keys(f"project:{project}:checkpoint:*")], reverse=True)

print(f"\n{'='*60}")
print(f"🍄 ALL CHECKPOINTS FOR: {project.upper()}")
print(f"{'='*60}\n")

if not checkpoint_keys:
    print("No checkpoints found.\n")
else:
    for i, key in enumerate(checkpoint_keys, 1):
        try:
            checkpoint = json.loads(r.get(key))
            summary = checkpoint.get('summary', '')
            timestamp = checkpoint.get('timestamp', 0)
            dt = datetime.fromtimestamp(timestamp)
            
            print(f"{i}. {summary}")
            print(f"   📅 {dt.strftime('%b %d, %Y at %I:%M %p PT')}\n")
        except:
            pass

print("="*60 + "\n")
