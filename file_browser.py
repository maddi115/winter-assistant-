import os
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

def browse_files(start_path="."):
    """Navigate directory and select file"""
    current_path = os.path.abspath(start_path)
    selected = 0
    
    while True:
        print("\033[2J\033[H")
        print("="*60)
        print(f"📂 FILE BROWSER")
        print("="*60)
        print(f"📍 {current_path}\n")
        
        items = ["📁 .."]  # Parent directory
        
        try:
            entries = sorted(os.listdir(current_path))
            for entry in entries:
                full_path = os.path.join(current_path, entry)
                if os.path.isdir(full_path):
                    items.append(f"📁 {entry}")
                else:
                    items.append(f"📄 {entry}")
        except PermissionError:
            items = ["❌ Permission denied"]
        
        for i, item in enumerate(items):
            if i == selected:
                print(f"  → {item}")
            else:
                print(f"    {item}")
        
        print("\n" + "="*60)
        print("W/S navigate | Enter select | Q back")
        
        key = get_key()
        
        if key in ['w', 'W', '\x1b[A']:
            selected = max(0, selected - 1)
        elif key in ['s', 'S', '\x1b[B']:
            selected = min(len(items) - 1, selected + 1)
        elif key in ['\r', '\n']:
            choice = items[selected]
            
            if choice == "📁 ..":
                current_path = os.path.dirname(current_path)
                selected = 0
            elif choice.startswith("📁"):
                folder = choice[2:].strip()
                current_path = os.path.join(current_path, folder)
                selected = 0
            elif choice.startswith("📄"):
                filename = choice[2:].strip()
                return os.path.join(current_path, filename)
        elif key in ['q', 'Q']:
            return None

def read_file(filepath, max_size=10000):
    """Read file with size limit"""
    try:
        size = os.path.getsize(filepath)
        if size > max_size:
            return f"File too large ({size} bytes). Max: {max_size} bytes"
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        return "Binary file (cannot display)"
    except Exception as e:
        return f"Error reading file: {e}"

if __name__ == "__main__":
    selected = browse_files(os.getcwd())
    if selected:
        print(f"\n✅ Selected: {selected}")
        print("\nContent preview:")
        print("="*60)
        print(read_file(selected)[:500])
