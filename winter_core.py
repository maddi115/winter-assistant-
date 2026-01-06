import redis
import subprocess
import json
import time

class WinterCore:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    def get_all_projects(self):
        all_keys = self.redis.keys('project:*')
        projects = {}
        for key in all_keys:
            parts = key.split(':')
            if len(parts) >= 2:
                proj = parts[1]
                if proj not in projects:
                    projects[proj] = 0
                projects[proj] += 1
        return projects
    
    def get_project_memory(self, project):
        memory = {}
        for key in self.redis.keys(f"project:{project}:*"):
            value = self.redis.get(key)
            if value:
                memory[key] = value
        return memory
    
    def sculpt_memory(self, project, user_input, assistant_response):
        prompt = f"""Analyze for project {project}:

User: {user_input}
Assistant: {assistant_response}

JSON only:
{{"immutable_facts": {{}}, "mutable_state": {{}}, "outcomes": []}}"""
        
        result = subprocess.run(['ollama', 'run', 'deepseek-r1:8b', prompt],
                              capture_output=True, text=True, timeout=30)
        
        try:
            text = result.stdout.split("...done thinking.")[-1].strip()
            text = text.replace('```json', '').replace('```', '').strip()
            data = json.loads(text)
            
            for k, v in data.get('immutable_facts', {}).items():
                self.redis.set(f"project:{project}:facts:{k}", json.dumps(v))
            
            for k, v in data.get('mutable_state', {}).items():
                self.redis.set(f"project:{project}:state:{k}", json.dumps(v))
            
            for i, o in enumerate(data.get('outcomes', [])):
                self.redis.set(f"project:{project}:outcomes:{int(time.time())}_{i}", json.dumps(o))
        except:
            pass
    
    def chat(self, project, user_input, memory):
        prompt = f"""You are agentWinter for {project}.

Memory: {json.dumps(memory, indent=2)}

User: {user_input}
agentWinter:"""
        
        process = subprocess.Popen(['ollama', 'run', 'deepseek-r1:8b', prompt],
                                  stdout=subprocess.PIPE, text=True, bufsize=1)
        
        response = ""
        for line in process.stdout:
            if "Thinking..." not in line and "...done thinking." not in line:
                yield line
                response += line
        
        return response
