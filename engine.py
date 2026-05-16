import requests
import re
import json
import time
import random
import os
import difflib
from urllib.parse import urlparse, urlunparse

class RiggingEngine:
    def __init__(self, projects_file="projects.json"):
        self.projects_file = projects_file
        self.load_projects()
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

    def load_projects(self):
        if os.path.exists(self.projects_file):
            with open(self.projects_file, 'r') as f:
                self.projects = json.load(f)
        else:
            self.projects = {"Default Project": {"url": "", "field_map": {}, "personas": {}, "pages": 0}}
            self.save_all()

    def save_all(self):
        with open(self.projects_file, 'w') as f:
            json.dump(self.projects, f, indent=4)

    def sanitize_url(self, url):
        parsed = urlparse(url)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

    def create_project(self, name, url=""):
        if name not in self.projects:
            self.projects[name] = {"url": url, "field_map": {}, "personas": {}, "pages": 0}
            self.save_all()
            return True
        return False

    def delete_project(self, name):
        if name in self.projects:
            del self.projects[name]
            self.save_all()
            return True
        return False

    def scrape_form(self, project_name, url):
        try:
            clean_url = self.sanitize_url(url)
            response = self.session.get(clean_url)
            
            # More robust data extraction
            match = re.search(r'FB_PUBLIC_LOAD_DATA_ = (.*?);', response.text, re.DOTALL)
            if not match: 
                return False, "Could not find FB_PUBLIC_LOAD_DATA. Form might be private."
            
            data = json.loads(match.group(1))
            
            # Find the questions list (it can be in different indices)
            questions = []
            try:
                # Common location
                questions = data[1][1]
            except:
                # Fallback search
                for item in data:
                    if isinstance(item, list) and len(item) > 1:
                        if isinstance(item[1], list) and len(item[1]) > 0:
                            questions = item[1]
                            break
            
            if not questions:
                return False, "Found form data but no questions detected."

            # Page Count detection
            pages_match = re.search(r'\[\[\d+,null,null,null,(\d+)\]', response.text)
            pages = int(pages_match.group(1)) if pages_match else 0
            
            field_map = {}
            for q in questions:
                try:
                    # q[1] is label, q[4][0][0] is entry_id
                    label = q[1]
                    entry_id = q[4][0][0]
                    required = q[4][0][2] if len(q[4][0]) > 2 else False
                    
                    options = []
                    # Check multiple locations for options (Radio/Checkbox)
                    if len(q[4][0]) > 1 and q[4][0][1]:
                        options = [opt[0] for opt in q[4][0][1]]
                    # Check for Linear Scale
                    elif len(q[4][0]) > 3 and q[4][0][3]:
                        options = [str(i) for i in range(1, 6)]
                    
                    key = f"entry.{entry_id}"
                    field_map[key] = {"label": label, "options": options, "required": required}
                except: continue
            
            self.projects[project_name]["url"] = clean_url
            self.projects[project_name]["field_map"] = field_map
            self.projects[project_name]["pages"] = pages
            self.save_all()
            return True, field_map
        except Exception as e:
            return False, f"Scrape Error: {str(e)}"

    def save_persona(self, project_name, persona_name, response_mapping):
        self.projects[project_name]["personas"][persona_name] = response_mapping
        self.save_all()

    def generate_persona(self, project_name, persona_name):
        proj = self.projects[project_name]
        field_map = proj["field_map"]
        persona_config = proj["personas"].get(persona_name, {})
        
        persona_data = {}
        for entry_id, info in field_map.items():
            label = info["label"].lower()
            options = info["options"]
            config = persona_config.get(entry_id, {})
            custom_values = config.get("values", [])
            
            if custom_values:
                val = random.choice(custom_values)
            elif options:
                val = random.choice(options)
            elif "email" in label:
                val = f"tester_{random.randint(100, 999)}@gmail.com"
            else:
                val = f"Insight {random.randint(10, 99)}"
            
            persona_data[entry_id] = val
        return persona_data

    def submit(self, project_name, payload, headers):
        proj = self.projects.get(project_name)
        if not proj: return False, "Project not found", {}
        
        url = proj["url"]
        form_url = url.replace("/viewform", "/formResponse")
        pages = proj.get("pages", 0)
        page_history = ",".join([str(i) for i in range(pages + 1)])
        
        try:
            resp = self.session.get(url, headers=headers)
            fbzx_m = re.search(r'name="fbzx"\s+value="([^"]+)"', resp.text)
            if not fbzx_m: return False, "fbzx token missing. Google blocked the GET request.", {}
            fbzx = fbzx_m.group(1)
            
            form_payload = [("fvv", "1"), ("pageHistory", page_history), ("fbzx", fbzx)]
            for eid, val in payload.items():
                if isinstance(val, list):
                    for v in val: form_payload.append((eid, str(v)))
                else:
                    form_payload.append((eid, str(val)))
            
            post_headers = headers.copy()
            post_headers["Content-Type"] = "application/x-www-form-urlencoded"
            res = self.session.post(form_url, data=form_payload, headers=post_headers)
            
            if res.status_code == 200 and "recorded" in res.text.lower():
                return True, "Success", {}
            else:
                return False, f"Status {res.status_code}", {"payload": form_payload, "response": res.text[:500]}
        except Exception as e:
            return False, f"Exception: {str(e)}", {}
