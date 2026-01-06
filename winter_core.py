import redis
import subprocess
import json
import time
import sys
import io

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
    
    def geocode(self, lat, lon):
        """Offline geocoding (suppress loading message)"""
        try:
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            import reverse_geocoder as rg
            result = rg.search((lat, lon))[0]
            
            sys.stdout = old_stdout
            
            return {
                'city': result['name'],
                'state': result['admin1'],
                'country': result['cc'],
                'formatted': f"{result['name']}, {result['admin1']}, {result['cc']}"
            }
        except:
            sys.stdout = old_stdout
            return None
    
    def detect_coordinates(self, text):
        """Detect coordinates in user input"""
        import re
        pattern = r'(-?\d+\.?\d*),\s*(-?\d+\.?\d*)'
        match = re.search(pattern, text)
        if match:
            lat, lon = float(match.group(1)), float(match.group(2))
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return (lat, lon)
        
        dms_pattern = r'(\d+)\s*deg\s*(\d+)\s*[\'\']\s*([\d.]+)\s*["\"]?\s*([NS]),?\s*(\d+)\s*deg\s*(\d+)\s*[\'\']\s*([\d.]+)\s*["\"]?\s*([EW])'
        dms_match = re.search(dms_pattern, text)
        if dms_match:
            lat_d, lat_m, lat_s, lat_dir = dms_match.group(1,2,3,4)
            lon_d, lon_m, lon_s, lon_dir = dms_match.group(5,6,7,8)
            
            lat = float(lat_d) + float(lat_m)/60 + float(lat_s)/3600
            lon = float(lon_d) + float(lon_m)/60 + float(lon_s)/3600
            
            if lat_dir == 'S': lat = -lat
            if lon_dir == 'W': lon = -lon
            
            return (lat, lon)
        
        return None
    
    def sculpt_memory(self, project, user_input, assistant_response):
        truncated_response = assistant_response[:500] if len(assistant_response) > 500 else assistant_response
        
        prompt = f"""Analyze conversation for project {project}.

User: {user_input[:200]}
AI: {truncated_response}

Extract key info as JSON only:
{{"immutable_facts": {{}}, "mutable_state": {{}}, "outcomes": []}}"""
        
        try:
            result = subprocess.run(['ollama', 'run', 'deepseek-r1:8b', prompt],
                                  capture_output=True, text=True, timeout=60)
            
            text = result.stdout
            if "...done thinking." in text:
                text = text.split("...done thinking.")[-1]
            
            text = text.strip().replace('```json', '').replace('```', '').strip()
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
        coords = self.detect_coordinates(user_input)
        
        memory_str = json.dumps(memory, indent=2)[:800] if memory else "{}"
        
        if coords:
            location = self.geocode(coords[0], coords[1])
            if location:
                # Store everything from tool
                self.redis.set(f"project:{project}:facts:latitude", json.dumps(coords[0]))
                self.redis.set(f"project:{project}:facts:longitude", json.dumps(coords[1]))
                self.redis.set(f"project:{project}:facts:location_full", json.dumps(location['formatted']))
                self.redis.set(f"project:{project}:facts:city", json.dumps(location['city']))
                self.redis.set(f"project:{project}:facts:state", json.dumps(location['state']))
                self.redis.set(f"project:{project}:facts:country", json.dumps(location['country']))
                
                prompt = f"""You are agentWinter, a helpful AI assistant.

Project: {project}
Memory: {memory_str}

User: {user_input}

[GEOCODING TOOL RESULT]
Coordinates: {coords[0]}, {coords[1]}
City: {location['city']}
State/Region: {location['state']}
Country: {location['country']}
Full Location: {location['formatted']}
[END TOOL RESULT]

Use the geocoding tool result above. Include the city, state, and country in your answer.

agentWinter:"""
            else:
                prompt = f"""You are agentWinter, a helpful AI assistant.

Project: {project}
Memory: {memory_str}

User: {user_input}
agentWinter:"""
        else:
            prompt = f"""You are agentWinter, a helpful AI assistant.

Project: {project}
Memory: {memory_str}

User: {user_input}
agentWinter:"""
        
        process = subprocess.Popen(
            ['ollama', 'run', 'deepseek-r1:8b', prompt],
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
