import redis
import subprocess
import json
import termios
import sys
import time

class ProjectAssistant:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.current_project = None
        
    def show_project_menu(self):
        # Get all projects
        all_keys = self.redis.keys('project:*')
        projects = sorted(set(p.split(':')[1] for p in all_keys if len(p.split(':')) >= 2))
        
        print("\n" + "="*60)
        print("📁 SELECT PROJECT")
        print("="*60 + "\n")
        
        if projects:
            for i, project in enumerate(projects, 1):
                key_count = len(self.redis.keys(f"project:{project}:*"))
                print(f"  {i}. {project} ({key_count} keys)")
        else:
            print("  No existing projects")
        
        print(f"\n  N. Create new project")
        print("="*60)
        
        choice = input("\nSelect (number or N): ").strip()
        
        if choice.upper() == 'N':
            new_name = input("Project name: ").strip()
            if new_name:
                self.current_project = new_name
                self.redis.set("current_project", new_name)
                print(f"\n✅ Created project: {new_name}")
        elif choice.isdigit() and 1 <= int(choice) <= len(projects):
            self.current_project = projects[int(choice) - 1]
            self.redis.set("current_project", self.current_project)
            print(f"\n✅ Loaded project: {self.current_project}")
        else:
            print("\n❌ Invalid choice")
            sys.exit(1)
    
    def get_project_memory(self):
        memory = {}
        pattern = f"project:{self.current_project}:*"
        for key in self.redis.keys(pattern):
            value = self.redis.get(key)
            if value:
                memory[key] = value
        return memory
    
    def sculpt_memory(self, user_input, assistant_response):
        prompt = f"""Analyze this conversation for project: {self.current_project}

User: {user_input}
Assistant: {assistant_response}

Extract as JSON:
{{
  "immutable_facts": {{"key": "value"}},
  "mutable_state": {{"key": {{"value": "...", "weight": 0.5}}}},
  "outcomes": ["insight"]
}}

JSON only:"""
        
        result = subprocess.run(
            ['ollama', 'run', 'deepseek-r1:8b', prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        try:
            response_text = result.stdout
            if "...done thinking." in response_text:
                response_text = response_text.split("...done thinking.")[-1]
            
            response_text = response_text.strip().replace('```json', '').replace('```', '').strip()
            memory_data = json.loads(response_text)
            
            for key, value in memory_data.get('immutable_facts', {}).items():
                self.redis.set(f"project:{self.current_project}:facts:{key}", json.dumps(value))
                print(f"  💾 [{self.current_project}] Saved fact: {key}")
            
            for key, data in memory_data.get('mutable_state', {}).items():
                self.redis.set(f"project:{self.current_project}:state:{key}", json.dumps(data))
                weight = data.get('weight', 0.5) if isinstance(data, dict) else 0.5
                print(f"  💾 [{self.current_project}] Saved state: {key} (weight: {weight})")
            
            outcomes = memory_data.get('outcomes', [])
            if outcomes:
                for i, outcome in enumerate(outcomes):
                    self.redis.set(f"project:{self.current_project}:outcomes:{int(time.time())}_{i}", json.dumps(outcome))
                print(f"  💾 [{self.current_project}] Saved {len(outcomes)} outcomes")
        except:
            pass
    
    def chat(self, user_input):
        if user_input.lower() == 'memory':
            subprocess.run(['python', 'view_project_memory.py', self.current_project])
            return
        
        if user_input.lower() == 'checkpoint':
            subprocess.run(['python', 'create_checkpoint.py'])
            return
        
        if user_input.lower() == 'checkpoint list':
            subprocess.run(['python', 'list_checkpoints.py'])
            return
        
        memory = self.get_project_memory()
        
        prompt = f"""You are agentWinter, assistant for project: {self.current_project}

Project Memory:
{json.dumps(memory, indent=2)}

User: {user_input}
agentWinter:"""
        
        start_time = time.time()
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        new_settings = termios.tcgetattr(fd)
        new_settings[3] = new_settings[3] & ~termios.ECHO & ~termios.ICANON
        termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
        
        process = subprocess.Popen(
            ['ollama', 'run', 'deepseek-r1:8b', prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1
        )
        
        print("\n🤖 ", end='', flush=True)
        response = ""
        show_output = False
        
        for line in process.stdout:
            if "Thinking..." in line:
                show_output = False
                continue
            if "...done thinking." in line:
                show_output = True
                continue
            
            if show_output or "Thinking..." not in response:
                print(line, end='', flush=True)
            response += line
        
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
        clean_response = response
        if "...done thinking." in clean_response:
            clean_response = clean_response.split("...done thinking.")[-1].strip()
        
        elapsed_time = time.time() - start_time
        print(f"\n\n⏱️  {elapsed_time:.2f}s")
        
        print(f"\n🧠 Sculpting memory for {self.current_project}...")
        self.sculpt_memory(user_input, clean_response)
        print()

assistant = ProjectAssistant()
assistant.show_project_menu()

print("\n" + "="*60)
print(f"🚀 WINTER ASSISTANT - {assistant.current_project.upper()}")
print("="*60)
print("Commands: 'memory', 'checkpoint', 'checkpoint list', 'quit'\n")

while True:
    try:
        user_input = input("💬 You: ").strip()
        if not user_input or user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!\n")
            break
        assistant.chat(user_input)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
        break
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
