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

def select_multiple_files(start_path="."):
    """Navigate directory and select multiple files"""
    current_path = os.path.abspath(start_path)
    selected_idx = 0
    selected_files = set()
    
    while True:
        print("\033[2J\033[H")
        print("="*60)
        print(f"📂 MULTI-FILE SELECTOR")
        print("="*60)
        print(f"📍 {current_path}")
        print(f"✅ Selected: {len(selected_files)} files\n")
        
        items = ["📁 ..", "✅ Done (finish selection)"]
        
        try:
            entries = sorted(os.listdir(current_path))
            for entry in entries:
                full_path = os.path.join(current_path, entry)
                if os.path.isdir(full_path):
                    items.append(f"📁 {entry}")
                else:
                    check = "✓" if full_path in selected_files else " "
                    items.append(f"[{check}] 📄 {entry}")
        except PermissionError:
            items = ["❌ Permission denied"]
        
        for i, item in enumerate(items):
            if i == selected_idx:
                print(f"  → {item}")
            else:
                print(f"    {item}")
        
        print("\n" + "="*60)
        print("W/S navigate | Space toggle file | Enter navigate/done | Q cancel")
        
        key = get_key()
        
        if key in ['w', 'W', '\x1b[A']:
            selected_idx = max(0, selected_idx - 1)
        elif key in ['s', 'S', '\x1b[B']:
            selected_idx = min(len(items) - 1, selected_idx + 1)
        elif key == ' ':  # Space to toggle
            choice = items[selected_idx]
            
            if choice.startswith("["):
                filename = choice.split("📄 ")[1]
                full_path = os.path.join(current_path, filename)
                
                if full_path in selected_files:
                    selected_files.remove(full_path)
                else:
                    selected_files.add(full_path)
        elif key in ['\r', '\n']:  # Enter
            choice = items[selected_idx]
            
            if choice == "✅ Done (finish selection)":
                if selected_files:
                    return list(selected_files)
            elif choice == "📁 ..":
                current_path = os.path.dirname(current_path)
                selected_idx = 0
            elif choice.startswith("📁") and not choice.startswith("📁 .."):
                folder = choice[2:].strip()
                current_path = os.path.join(current_path, folder)
                selected_idx = 0
            # Files don't do anything on Enter - use Space to toggle
        elif key in ['q', 'Q']:
            return None

def read_multiple_files(filepaths, max_size=5000):
    """Read multiple files and combine"""
    combined = ""
    for path in filepaths:
        try:
            size = os.path.getsize(path)
            if size > max_size:
                combined += f"\n\n--- {os.path.basename(path)} (too large: {size} bytes) ---\n"
                continue
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                combined += f"\n\n--- {os.path.basename(path)} ---\n{content}\n"
        except:
            combined += f"\n\n--- {os.path.basename(path)} (error reading) ---\n"
    
    return combined

if __name__ == "__main__":
    files = select_multiple_files(os.getcwd())
    if files:
        print(f"\n✅ Selected {len(files)} files:")
        for f in files:
            print(f"  - {f}")
