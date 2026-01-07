import sys
import tty
import termios

def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def show_header(project):
    """Show conversation header"""
    print("\033[2J\033[H")
    print("="*60)
    print(f"🚀 WINTER ASSISTANT (LanceDB) - {project}")
    print("="*60)
    print("\nCommands: history | search <query> | quit\n")

def show_main_menu(projects):
    """Main menu for LanceDB assistant"""
    options = [
        "💬 New conversation",
        "📁 Browse file (single)",
        "📂 Browse files (multiple)",
    ]
    
    # Add existing projects
    for proj in sorted(projects.keys()):
        options.append(f"📊 Project: {proj} ({projects[proj]} keys)")
    
    options.extend([
        "🆕 Create new project",
        "❌ Quit"
    ])
    
    selected = 0
    
    while True:
        print("\033[2J\033[H")
        print("="*60)
        print("🚀 WINTER ASSISTANT - LANCEDB MODE")
        print("="*60)
        print("\nVector search enabled • Semantic retrieval\n")
        
        for i, option in enumerate(options):
            if i == selected:
                print(f"  → {option}")
            else:
                print(f"    {option}")
        
        print("\n" + "="*60)
        print("W/S navigate | Enter select | Q quit")
        
        key = get_key()
        
        if key in ['w', 'W', '\x1b[A']:
            selected = (selected - 1) % len(options)
        elif key in ['s', 'S', '\x1b[B']:
            selected = (selected + 1) % len(options)
        elif key in ['\r', '\n']:
            if selected == 0:
                return ("new_conversation", None)
            elif selected == 1:
                import file_browser
                filepath = file_browser.browse()
                if filepath:
                    return ("browse_file", filepath)
            elif selected == 2:
                import multi_file_selector
                filepaths = multi_file_selector.select_files()
                if filepaths:
                    return ("browse_files", filepaths)
            elif selected < len(options) - 2:
                # Existing project
                proj_index = selected - 3
                proj_name = sorted(projects.keys())[proj_index]
                return ("existing_project", proj_name)
            elif selected == len(options) - 2:
                # New project
                print("\033[2J\033[H")
                name = input("\n📝 Project name: ").strip()
                if name:
                    return ("new_project", name)
            else:
                # Quit
                return (None, None)
        elif key in ['q', 'Q']:
            return (None, None)

def file_action_menu():
    """Menu for file actions"""
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
