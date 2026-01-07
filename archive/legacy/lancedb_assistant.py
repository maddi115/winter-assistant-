#!/usr/bin/env python
import sys
import time
from winter_core import WinterCore
from lancedb_ui import show_main_menu, show_header, file_action_menu
from lancedb_conversation_manager import LanceDBConversationManager
import conversation_selector
import file_browser
import multi_file_selector

core = WinterCore()

# Main menu
projects = core.get_all_projects()
action, value = show_main_menu(projects)

# Handle file browsing (single or multiple)
if action in ["browse_file", "browse_files"]:
    if action == "browse_file":
        filepath = value
        file_content = file_browser.read_file(filepath)
    else:  # browse_files
        filepaths = value
        file_content = multi_file_selector.read_multiple_files(filepaths)

    file_action = file_action_menu()

    if not file_action:
        sys.exit(0)

    project = "file_analysis"

    if file_action == "analyze":
        user_input = f"Analyze these files:\n\n{file_content}"
    elif file_action == "question":
        print("\033[2J\033[H")
        question = input("\n❓ Your question: ").strip()
        user_input = f"File content:\n{file_content}\n\nQuestion: {question}"

    # Show conversation selector
    conv_action, conv_id = conversation_selector.show_conversation_menu(project)
    
    if not conv_action:
        sys.exit(0)
    
    if conv_action == "new":
        conv = LanceDBConversationManager(project)
    else:
        conv = LanceDBConversationManager(project, conversation_id=conv_id)
        # Show loaded conversation
        turns = conv.get_all_turns()
        if turns:
            print(f"\n📜 Loaded: {turns[0]['title']} ({len(turns)} turns)\n")
            time.sleep(1)

elif action == "new_conversation":
    project = "conversations"
    
    # Show conversation selector
    conv_action, conv_id = conversation_selector.show_conversation_menu(project)
    
    if not conv_action:
        sys.exit(0)
    
    if conv_action == "new":
        conv = LanceDBConversationManager(project)
    else:
        conv = LanceDBConversationManager(project, conversation_id=conv_id)
        turns = conv.get_all_turns()
        if turns:
            print(f"\n📜 Loaded: {turns[0]['title']} ({len(turns)} turns)\n")
            time.sleep(1)

elif action == "new_project":
    project = value
    
    conv_action, conv_id = conversation_selector.show_conversation_menu(project)
    
    if not conv_action:
        sys.exit(0)
    
    if conv_action == "new":
        conv = LanceDBConversationManager(project)
    else:
        conv = LanceDBConversationManager(project, conversation_id=conv_id)
        turns = conv.get_all_turns()
        if turns:
            print(f"\n📜 Loaded: {turns[0]['title']} ({len(turns)} turns)\n")
            time.sleep(1)

elif action == "existing_project":
    project = value
    
    conv_action, conv_id = conversation_selector.show_conversation_menu(project)
    
    if not conv_action:
        sys.exit(0)
    
    if conv_action == "new":
        conv = LanceDBConversationManager(project)
    else:
        conv = LanceDBConversationManager(project, conversation_id=conv_id)
        turns = conv.get_all_turns()
        if turns:
            print(f"\n📜 Loaded: {turns[0]['title']} ({len(turns)} turns)\n")
            time.sleep(1)
else:
    sys.exit(1)

if not project:
    sys.exit(1)

show_header(project)

# If file selected, process it first
if action in ["browse_file", "browse_files"]:
    memory = {}
    
    # RAG: Get recent turns + semantic search
    recent_turns = conv.get_recent_turns(3)
    relevant_turns = conv.search_conversations(user_input, limit=3, current_conversation_only=True)
    
    # Combine and deduplicate
    all_turn_ids = set()
    conversation_history = []
    
    for turn in recent_turns:
        turn_id = f"{turn['timestamp']}_{turn['turn_number']}"
        if turn_id not in all_turn_ids:
            all_turn_ids.add(turn_id)
            conversation_history.append(turn)
    
    for turn in relevant_turns:
        turn_id = f"{turn['timestamp']}_{turn['turn_number']}"
        if turn_id not in all_turn_ids:
            all_turn_ids.add(turn_id)
            conversation_history.append(turn)
    
    # Sort by timestamp
    conversation_history.sort(key=lambda x: x['timestamp'])

    print("\n🤖 ", end='', flush=True)
    start = time.time()
    response = ""

    for chunk in core.chat(project, user_input, memory, conversation_history):
        print(chunk, end='', flush=True)
        response += chunk

    elapsed = time.time() - start
    print(f"\n\n⏱️  {elapsed:.2f}s\n")

    conv.save_turn(user_input, response, elapsed)

# Chat loop
while True:
    try:
        user_input = input("💬 You: ").strip()
        if not user_input or user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!\n")
            break

        if user_input.lower() == 'memory':
            import subprocess
            subprocess.run(['python', 'view_project_memory.py', project])
            continue

        if user_input.lower() == 'checkpoint':
            import subprocess
            subprocess.run(['python', 'create_checkpoint.py'])
            continue

        if user_input.lower() == 'history':
            turns = conv.get_recent_turns(10)
            print("\n📜 RECENT CONVERSATION\n")
            for t in turns:
                print(f"[{t['datetime']}]")
                print(f"You: {t['user'][:50]}...")
                print(f"AI: {t['assistant'][:80]}...")
                print()
            continue

        if user_input.lower().startswith('search '):
            query = user_input[7:].strip()
            print(f"\n🔍 Searching for: {query}\n")
            
            results = conv.search_conversations(query, limit=5)
            
            if not results:
                print("No results found.\n")
            else:
                for i, r in enumerate(results, 1):
                    print(f"📍 Result {i} - {r['title']} (Turn {r['turn_number']})")
                    print(f"   [{r['datetime']}]")
                    print(f"   You: {r['user'][:60]}...")
                    print(f"   AI: {r['assistant'][:80]}...")
                    print()
            continue

        memory = core.get_project_memory(project) if action not in ["new_conversation", "browse_file", "browse_files"] else {}
        
        # RAG: Get recent context + semantically relevant context
        recent_turns = conv.get_recent_turns(3)  # Last 3 turns for recency
        relevant_turns = conv.search_conversations(user_input, limit=3, current_conversation_only=True)  # 3 relevant turns
        
        # Combine and deduplicate by timestamp + turn_number
        all_turn_ids = set()
        conversation_history = []
        
        # Add recent turns first
        for turn in recent_turns:
            turn_id = f"{turn['timestamp']}_{turn['turn_number']}"
            if turn_id not in all_turn_ids:
                all_turn_ids.add(turn_id)
                conversation_history.append(turn)
        
        # Add relevant turns (if not already included)
        for turn in relevant_turns:
            turn_id = f"{turn['timestamp']}_{turn['turn_number']}"
            if turn_id not in all_turn_ids:
                all_turn_ids.add(turn_id)
                conversation_history.append(turn)
        
        # Sort by timestamp to maintain chronological order
        conversation_history.sort(key=lambda x: x['timestamp'])

        print("\n🤖 ", end='', flush=True)
        start = time.time()
        response = ""

        for chunk in core.chat(project, user_input, memory, conversation_history):
            print(chunk, end='', flush=True)
            response += chunk

        elapsed = time.time() - start
        print(f"\n\n⏱️  {elapsed:.2f}s\n")

        conv.save_turn(user_input, response, elapsed)

        if action not in ["new_conversation", "browse_file", "browse_files"]:
            print("🧠 Sculpting memory...")
            core.sculpt_memory(project, user_input, response)
        print()

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
        break
