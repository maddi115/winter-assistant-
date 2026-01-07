import sys
import tty
import termios
import subprocess
import os
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

def open_folder():
    folder = os.path.expanduser("~/winter-assistant")
    wsl_path = subprocess.run(['wslpath', '-w', folder], capture_output=True, text=True).stdout.strip()
    subprocess.run(['explorer.exe', wsl_path])

def export_project_menu(projects):
    items = sorted(projects.keys())
    if not items:
        print("\n❌ No projects to export")
        input("Press Enter to continue...")
        return None
    
    selected = 0
    
    while True:
        print("\033[2J\033[H")
        print("="*60)
        print("📤 SELECT PROJECT TO EXPORT")
        print("="*60 + "\n")
        
        for i, item in enumerate(items):
            if i == selected:
                print(f"  → {item}")
            else:
                print(f"    {item}")
        
        print("\n" + "="*60)
        print("W/S navigate | Enter select | Q back")
        
        key = get_key()
        
        if key in ['w', 'W', '\x1b[A']:
            selected = (selected - 1) % len(items)
        elif key in ['s', 'S', '\x1b[B']:
            selected = (selected + 1) % len(items)
        elif key in ['\r', '\n']:
            return items[selected]
        elif key in ['q', 'Q']:
            return None

def export_project(project):
    import redis
    import json
    
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    data = {}
    for key in r.keys(f"project:{project}:*"):
        data[key] = r.get(key)
    
    os.makedirs('exports', exist_ok=True)
    with open(f"exports/{project}.json", 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✅ Exported to exports/{project}.json")
    input("\nPress Enter to continue...")

def show_file_browser():
    return file_browser.browse_files(os.path.expanduser("~/winter-assistant"))

def show_multi_file_browser():
    return multi_file_selector.select_multiple_files(os.path.expanduser("~/winter-assistant"))

def show_main_menu(projects):
    items = sorted(projects.keys()) + [
        "💬 New conversation",
        "➕ Create new project",
        "📂 Browse file",
        "📋 Select multiple files",
        "📤 Export project",
        "📁 Open folder"
    ]
    selected = 0
    
    while True:
        print("\033[2J\033[H")
        print("="*60)
        print("📁 WINTER ASSISTANT")
        print("="*60 + "\n")
        
        for i, item in enumerate(items):
            if i == selected:
                if i < len(projects):
                    keys = projects[item]
                    print(f"  → {item} ({keys} keys)")
                else:
                    print(f"  → {item}")
            else:
                if i < len(projects):
                    keys = projects[item]
                    print(f"    {item} ({keys} keys)")
                else:
                    print(f"    {item}")
        
        print("\n" + "="*60)
        print("W/S navigate | Enter select | Q quit")
        
        key = get_key()
        
        if key in ['w', 'W', '\x1b[A']:
            selected = (selected - 1) % len(items)
        elif key in ['s', 'S', '\x1b[B']:
            selected = (selected + 1) % len(items)
        elif key in ['\r', '\n']:
            if items[selected] == "📂 Browse file":
                filepath = show_file_browser()
                if filepath:
                    return ("browse_file", filepath)
                continue
            elif items[selected] == "📋 Select multiple files":
                filepaths = show_multi_file_browser()
                if filepaths:
                    return ("browse_files", filepaths)
                continue
            elif items[selected] == "📁 Open folder":
                open_folder()
                continue
            elif items[selected] == "📤 Export project":
                proj = export_project_menu(projects)
                if proj:
                    export_project(proj)
                continue
            elif items[selected] == "💬 New conversation":
                return ("new_conversation", None)
            elif items[selected] == "➕ Create new project":
                print("\033[2J\033[H")
                name = input("\n📝 New project name: ").strip()
                return ("new_project", name)
            else:
                return ("existing_project", items[selected])
        elif key in ['q', 'Q']:
            sys.exit(0)

def show_header(project):
    print("\n" + "="*60)
    print(f"🚀 WINTER ASSISTANT - {project.upper()}")
    print("="*60)
    print("Commands: memory, checkpoint, history, quit\n")
