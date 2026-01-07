"""Reusable UI components"""
import sys
import tty
import termios

def get_key():
    """Get single keypress"""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def clear_screen():
    """Clear terminal"""
    print("\033[2J\033[H", end='')

def menu(title: str, options: list, selected: int = 0) -> int:
    """Generic menu renderer"""
    clear_screen()
    print("="*60)
    print(title)
    print("="*60 + "\n")
    
    for i, option in enumerate(options):
        if i == selected:
            print(f"  → {option}")
        else:
            print(f"    {option}")
    
    print("\n" + "="*60)
    return selected
