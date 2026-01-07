"""Simple JSONL fallback storage - no embeddings required"""
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any
import uuid

from storage.base import BaseStorage
from core.errors import StorageError

class JSONLStorage(BaseStorage):
    """Simple JSONL storage - fallback when LanceDB fails"""
    
    def __init__(self, config):
        super().__init__(config)
        self.storage_dir = "./conversations_fallback"
        os.makedirs(self.storage_dir, exist_ok=True)
        
        self.conversation_id = str(uuid.uuid4())
        self.session = int(time.time())
        self.turn_number = 0
        self.file_path = f"{self.storage_dir}/{self.project}.jsonl"
    
    def save_turn(self, user_msg: str, ai_msg: str, metadata: Dict[str, Any]) -> None:
        """Save turn to JSONL"""
        try:
            turn = {
                "conversation_id": self.conversation_id,
                "timestamp": time.time(),
                "datetime": datetime.now().strftime("%Y-%m-%d %I:%M %p PT"),
                "session": self.session,
                "project": self.project,
                "turn_number": self.turn_number,
                "user": user_msg,
                "assistant": ai_msg,
                "elapsed": metadata.get('elapsed', 0.0)
            }
            
            with open(self.file_path, 'a') as f:
                f.write(json.dumps(turn) + '\n')
            
            self.turn_number += 1
        except Exception as e:
            raise StorageError(f"JSONL save failed: {e}")
    
    def get_recent(self, limit: int) -> List[Dict[str, Any]]:
        """Get recent turns"""
        try:
            if not os.path.exists(self.file_path):
                return []
            
            with open(self.file_path, 'r') as f:
                lines = f.readlines()
            
            turns = [json.loads(l) for l in lines if l.strip()]
            # Filter by current conversation
            conv_turns = [t for t in turns if t['conversation_id'] == self.conversation_id]
            return conv_turns[-limit:]
        except Exception as e:
            return []
    
    def get_all_turns(self) -> List[Dict[str, Any]]:
        """Get all turns"""
        return self.get_recent(1000)
    
    def search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Simple keyword search (no embeddings)"""
        try:
            all_turns = self.get_recent(1000)
            # Simple keyword matching
            query_lower = query.lower()
            matches = [
                t for t in all_turns 
                if query_lower in t['user'].lower() or query_lower in t['assistant'].lower()
            ]
            return matches[-limit:]
        except:
            return []
