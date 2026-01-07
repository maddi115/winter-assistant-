import json
import time
from datetime import datetime

class ConversationManager:
    def __init__(self, project_name):
        self.project = project_name
        self.conv_file = f"conversations/{project_name}.jsonl"
        self.current_session = int(time.time())
    
    def save_turn(self, user_msg, assistant_msg, elapsed_time):
        """Save full conversation turn"""
        import os
        os.makedirs('conversations', exist_ok=True)
        
        turn = {
            "timestamp": time.time(),
            "datetime": datetime.now().strftime("%Y-%m-%d %I:%M %p PT"),
            "session": self.current_session,
            "project": self.project,
            "user": user_msg,
            "assistant": assistant_msg,
            "elapsed": elapsed_time
        }
        
        with open(self.conv_file, 'a') as f:
            f.write(json.dumps(turn) + '\n')
    
    def get_recent_turns(self, n=10):
        """Get last N conversation turns"""
        try:
            with open(self.conv_file, 'r') as f:
                lines = f.readlines()
                return [json.loads(l) for l in lines[-n:]]
        except:
            return []
    
    def list_sessions(self):
        """Get all unique sessions"""
        try:
            sessions = {}
            with open(self.conv_file, 'r') as f:
                for line in f:
                    turn = json.loads(line)
                    sess = turn['session']
                    if sess not in sessions:
                        sessions[sess] = {
                            'start': turn['datetime'],
                            'turns': 0
                        }
                    sessions[sess]['turns'] += 1
            return sessions
        except:
            return {}
