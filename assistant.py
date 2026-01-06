#!/usr/bin/env python
import sys
import time
import tty
import termios
from winter_core import WinterCore
from winter_ui import show_main_menu, show_header
from conversation_manager import ConversationManager
import file_browser
import multi_file_selector

def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def file_action_menu():
    options = ["📖 Read and analyze", "❓ Ask questions about it", "❌ Cancel"]
    selected = 0
    
    while True:
        print("\033[2J\033[H")
        print("="*60)
        print("📄 WHAT TO DO WITH FILES?")
        print("="*60 + "\n")
        
        for i, option in enumerate(options):
            if i == selected:
                print(f"  → {option}")
            else:
                print(f"    {option}")
        
        print("\n" + "="*60)
        print("W/S navigate | Enter select | Q cancel")
        
        key = get_key()
        
        if key in ['w', 'W', '\x1b[A']:
            selected = (selected - 1) % len(options)
        elif key in ['s', 'S', '\x1b[B']:
            selected = (selected + 1) % len(options)
        elif key in ['\r', '\n']:
            if selected == 0:
                return "analyze"
            elif selected == 1:
                return "question"
            else:
                return None
        elif key in ['q', 'Q']:
            return None

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
    
    conv = ConversationManager(project)
    
elif action == "new_conversation":
    project = "conversations"
    conv = ConversationManager(project)
elif action == "new_project":
    project = value
    conv = ConversationManager(project)
elif action == "existing_project":
    project = value
    conv = ConversationManager(project)
else:
    sys.exit(1)

if not project:
    sys.exit(1)

show_header(project)

# If file selected, process it first
if action in ["browse_file", "browse_files"]:
    memory = {}
    
    print("\n🤖 ", end='', flush=True)
    start = time.time()
    response = ""
    
    for chunk in core.chat(project, user_input, memory):
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
        
        memory = core.get_project_memory(project) if action not in ["new_conversation", "browse_file", "browse_files"] else {}
        
        print("\n🤖 ", end='', flush=True)
        start = time.time()
        response = ""
        
        for chunk in core.chat(project, user_input, memory):
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
