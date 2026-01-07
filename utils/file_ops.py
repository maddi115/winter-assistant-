"""File operations utilities"""
import os
from typing import Optional, List

def read_file(filepath: str, max_size: int = 10000) -> str:
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

def list_files(directory: str) -> List[str]:
    """List files in directory"""
    try:
        return sorted(os.listdir(directory))
    except Exception:
        return []
