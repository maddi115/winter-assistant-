"""AI inference engine - isolated from storage/UI"""
import subprocess
from typing import List, Dict, Any, Iterator
from core.interfaces import AIInterface
from core.errors import AIError

class OllamaAI(AIInterface):
    """Ollama-based AI implementation"""
    
    def __init__(self, config):
        self.model = config.ai_model
    
    def generate(self, user_input: str, context: List[Dict[str, Any]]) -> Iterator[str]:
        """Generate streaming response with context"""
        
        # Build conversation history from context
        history_str = ""
        if context:
            for turn in context[-5:]:  # Last 5 for token efficiency
                history_str += f"\nUser: {turn['user']}\nagentWinter: {turn['assistant']}\n"
        
        # FIXED PRONOUN BUG: Clear instructions about user vs AI identity
        prompt = f"""You are agentWinter, a helpful AI assistant.

IMPORTANT: When users share information about themselves, remember it's THEIR information, not yours.
- If user says "my name is John" → respond "Nice to meet you, John!" (NOT "My name is John")
- You are agentWinter. The user has their own separate identity.

Conversation History:{history_str}

User: {user_input}
agentWinter:"""
        
        try:
            process = subprocess.Popen(
                ['ollama', 'run', self.model, prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1
            )
            
            in_thinking = False
            for line in process.stdout:
                if "Thinking..." in line:
                    in_thinking = True
                    continue
                if "...done thinking." in line:
                    in_thinking = False
                    continue
                if not in_thinking:
                    yield line
                    
        except Exception as e:
            raise AIError(f"AI generation failed: {e}")
