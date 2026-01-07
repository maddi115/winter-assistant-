import redis
import time
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
project = r.get("current_project")

content = "Context preservation is paramount to all memory decisions"

print(f"\n⚠️  ADDING TO SACRED FOUNDATION")
print("="*60)
print(f"Content: {content}")
print("="*60)
confirm = input("\n🔐 This becomes IMMUTABLE core context. Confirm? (yes/no): ").strip().lower()

if confirm == 'yes':
    foundation_key = f"project:{project}:foundation:core"
    existing = r.get(foundation_key)
    
    if existing:
        foundation_data = json.loads(existing)
    else:
        foundation_data = {"principles": [], "established": int(time.time())}
    
    foundation_data["principles"].append({
        "content": content,
        "timestamp": int(time.time()),
        "locked": True
    })
    
    r.set(foundation_key, json.dumps(foundation_data))
    print("\n✅ Added to SACRED FOUNDATION 🗿\n")
else:
    print("\n❌ Cancelled\n")
