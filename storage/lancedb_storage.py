"""LanceDB storage implementation"""
import lancedb
import uuid
import time
import os
from datetime import datetime
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

from storage.base import BaseStorage
from core.errors import StorageError

class LanceDBStorage(BaseStorage):
    """LanceDB vector storage with embeddings"""
    
    def __init__(self, config):
        super().__init__(config)
        
        try:
            print("🔄 Loading embedding model...")
            self.model = SentenceTransformer(config.embedding_model)
            
            os.makedirs(config.storage_path, exist_ok=True)
            self.db = lancedb.connect(config.storage_path)
            
            try:
                self.table = self.db.open_table('conversations')
            except:
                schema = {
                    "conversation_id": "",
                    "title": "",
                    "timestamp": 0.0,
                    "datetime": "",
                    "session": 0,
                    "project": "",
                    "turn_number": 0,
                    "user": "",
                    "assistant": "",
                    "elapsed": 0.0,
                    "vector": [0.0] * 384
                }
                self.table = self.db.create_table('conversations', [schema])
            
            self.conversation_id = str(uuid.uuid4())
            self.session = int(time.time())
            self.turn_number = 0
            
        except Exception as e:
            raise StorageError(f"LanceDB initialization failed: {e}")
    
    def save_turn(self, user_msg: str, ai_msg: str, metadata: Dict[str, Any]) -> None:
        """Save turn with embedding"""
        try:
            # Generate title on first turn
            if self.turn_number == 0:
                title = self._generate_title(user_msg, ai_msg)
            else:
                result = self.table.search() \
                    .where(f"conversation_id = '{self.conversation_id}'") \
                    .limit(1).to_pandas()
                title = result.iloc[0]['title'] if len(result) > 0 else "Conversation"
            
            # Embed conversation turn
            combined = f"user: {user_msg} | assistant: {ai_msg}"
            vector = self.model.encode(combined).tolist()
            
            turn = {
                "conversation_id": self.conversation_id,
                "title": title,
                "timestamp": time.time(),
                "datetime": datetime.now().strftime("%Y-%m-%d %I:%M %p PT"),
                "session": self.session,
                "project": self.project,
                "turn_number": self.turn_number,
                "user": user_msg,
                "assistant": ai_msg,
                "elapsed": metadata.get('elapsed', 0.0),
                "vector": vector
            }
            
            self.table.add([turn])
            self.turn_number += 1
            
        except Exception as e:
            raise StorageError(f"Save failed: {e}")
    
    def get_recent(self, limit: int) -> List[Dict[str, Any]]:
        """Get recent turns from current conversation"""
        try:
            result = self.table.search() \
                .where(f"conversation_id = '{self.conversation_id}'") \
                .limit(1000).to_pandas()
            
            if len(result) == 0:
                return []
            
            turns = result.sort_values('turn_number').to_dict('records')
            return turns[-limit:] if turns else []
        except Exception as e:
            raise StorageError(f"Get recent failed: {e}")
    
    def get_all_turns(self) -> List[Dict[str, Any]]:
        """Get all turns from current conversation"""
        try:
            result = self.table.search() \
                .where(f"conversation_id = '{self.conversation_id}'") \
                .limit(1000).to_pandas()
            
            if len(result) == 0:
                return []
            
            return result.sort_values('turn_number').to_dict('records')
        except Exception as e:
            return []
    
    def search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Semantic search across conversations"""
        try:
            query_vector = self.model.encode(query).tolist()
            search = self.table.search(query_vector).limit(limit)
            search = search.where(f"conversation_id = '{self.conversation_id}'")
            
            results = search.to_pandas().to_dict('records')
            return results
        except Exception as e:
            raise StorageError(f"Search failed: {e}")
    
    def _generate_title(self, user_msg: str, ai_msg: str) -> str:
        """Generate 3-word title using ollama"""
        import subprocess
        
        print("🏷️  Generating conversation title...")
        prompt = f"""Generate a 3-word title for this conversation. Only output 3 words, nothing else.

User: {user_msg[:100]}
AI: {ai_msg[:100]}

3-word title:"""
        
        try:
            result = subprocess.run(
                ['ollama', 'run', 'deepseek-r1:8b', prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            title = result.stdout.strip()
            if "...done thinking." in title:
                title = title.split("...done thinking.")[-1].strip()
            
            words = title.strip().split()[:3]
            title = " ".join(words)
            
            print(f"📝 Title: {title}")
            return title
        except:
            return "Conversation"
    
    def list_conversations(self, project: str = None) -> List[Dict[str, Any]]:
        """List all conversations"""
        try:
            if project:
                result = self.table.search() \
                    .where(f"project = '{project}'") \
                    .limit(10000).to_pandas()
            else:
                result = self.table.search().limit(10000).to_pandas()
            
            if len(result) == 0:
                return []
            
            conversations = {}
            for _, row in result.iterrows():
                conv_id = row['conversation_id']
                if conv_id not in conversations:
                    conversations[conv_id] = {
                        'conversation_id': conv_id,
                        'title': row['title'],
                        'project': row['project'],
                        'turns': 0,
                        'last_updated': row['datetime']
                    }
                conversations[conv_id]['turns'] += 1
            
            return list(conversations.values())
        except Exception as e:
            print(f"Error listing conversations: {e}")
            return []
