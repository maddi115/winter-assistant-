import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

project_name = "memory_system_testing"

# Get all non-project keys
all_keys = r.keys('*')
migrated = 0

for key in all_keys:
    # Skip if already a project key or system keys
    if key.startswith('project:') or key == 'current_project':
        continue
    
    # Get the value
    value = r.get(key)
    if value:
        # Create new project-specific key
        new_key = f"project:{project_name}:{key}"
        r.set(new_key, value)
        migrated += 1
        print(f"✓ Migrated: {key} → {new_key}")

print(f"\n✅ Migrated {migrated} keys to project '{project_name}'")
print("\n🗑️  Delete old keys? (y/n): ", end='')
import sys
choice = input().strip().lower()
if choice == 'y':
    deleted = 0
    for key in all_keys:
        if not key.startswith('project:') and key != 'current_project':
            r.delete(key)
            deleted += 1
    print(f"✅ Deleted {deleted} old keys")
else:
    print("Old keys kept (they won't interfere)")

# Set current project
r.set("current_project", project_name)
print(f"\n📁 Current project set to: {project_name}")
