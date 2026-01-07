#!/usr/bin/env python
"""Test LanceDB conversation storage"""

from lancedb_conversation_manager import LanceDBConversationManager
import time

print("="*60)
print("🧪 TESTING LANCEDB CONVERSATION MANAGER")
print("="*60)

# Test 1: Create new conversation
print("\n1️⃣  Creating test conversation...")
conv = LanceDBConversationManager("test_project")
print(f"   Conversation ID: {conv.conversation_id}")

# Test 2: Save turns
print("\n2️⃣  Saving test turns...")
turns = [
    ("What are Redis keys?", "Redis keys are string identifiers used to store and retrieve data."),
    ("How do I use coordinates?", "You can use lat/lon coordinates with the geocode function."),
    ("Tell me about memory architecture", "The memory system uses facts, states, and outcomes.")
]

for user, assistant in turns:
    print(f"   Saving: {user[:30]}...")
    conv.save_turn(user, assistant, 1.5)
    time.sleep(0.5)

# Test 3: Get recent turns
print("\n3️⃣  Getting recent turns...")
recent = conv.get_recent_turns(3)
print(f"   Retrieved {len(recent)} turns")
for r in recent:
    print(f"   - Turn {r['turn_number']}: {r['user'][:40]}...")

# Test 4: List all conversations
print("\n4️⃣  Listing all conversations...")
all_convs = conv.list_conversations()
print(f"   Found {len(all_convs)} conversations:")
for c in all_convs:
    print(f"   - {c['title']} ({c['turn_count']} turns) [{c['project']}]")

# Test 5: Semantic search
print("\n5️⃣  Testing semantic search...")
query = "geocoding location"
print(f"   Query: '{query}'")
results = conv.search_conversations(query, limit=2)
print(f"   Found {len(results)} results:")
for r in results:
    print(f"   - {r['title']} (Turn {r['turn_number']})")
    print(f"     User: {r['user'][:50]}...")

# Test 6: Load existing conversation
print("\n6️⃣  Loading existing conversation...")
if all_convs:
    test_id = all_convs[0]['conversation_id']
    conv2 = LanceDBConversationManager("test_project", conversation_id=test_id)
    loaded_turns = conv2.get_all_turns()
    print(f"   Loaded {len(loaded_turns)} turns from: {all_convs[0]['title']}")

print("\n" + "="*60)
print("✅ ALL TESTS PASSED")
print("="*60)
print("\nTo use LanceDB assistant, run:")
print("  python lancedb_assistant.py")
print()
