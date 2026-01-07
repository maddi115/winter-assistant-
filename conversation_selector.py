import sys
import tty
import termios
from lancedb_conversation_manager import LanceDBConversationManager

def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def show_conversation_menu(project):
    """Show menu to select or create conversation"""
    
    # Get list of conversations for this project
    temp_conv = LanceDBConversationManager(project)
    conversations = temp_conv.list_conversations(project)
    
    options = ["🆕 Start new conversation"]
    conv_ids = [None]
    
    for c in conversations:
        options.append(
            f"📝 {c['title']} ({c['last_updated']}) - {c['turns']} turns"
        )
        conv_ids.append(c['conversation_id'])
    
    options.append("❌ Cancel")
    conv_ids.append(None)
    
    selected = 0
    
    while True:
        print("\033[2J\033[H")
        print("="*60)
        print(f"🗂️  SELECT CONVERSATION - {project}")
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
                return ("new", None)
            elif selected == len(options) - 1:
                return (None, None)
            else:
                return ("existing", conv_ids[selected])
        elif key in ['q', 'Q']:
            return (None, None)
