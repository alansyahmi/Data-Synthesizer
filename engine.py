import requests
import re
import json
import time
import random
import os
import difflib
from urllib.parse import urlparse, urlunparse

class RiggingEngine:
    def __init__(self, projects_file=None):
        if projects_file is None:
            try:
                import streamlit as st
                self.projects_file = st.secrets.get("PROJECTS_FILE", "projects.json")
            except Exception:
                self.projects_file = "projects.json"
        else:
            self.projects_file = projects_file
        self.banned_emails_file = "banned_emails.json"
        self.load_projects()
        self.load_banned_emails()
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

    def load_projects(self):
        if os.path.exists(self.projects_file):
            with open(self.projects_file, 'r') as f:
                self.projects = json.load(f)
            if self.migrate_legacy_projects():
                self.save_all()
        else:
            self.projects = {"Default Project": {"url": "", "field_map": {}, "personas": {}, "pages": 0}}
            self.save_all()

    def migrate_legacy_projects(self):
        migrated_any = False
        for project_name, project_data in self.projects.items():
            field_map = project_data.get("field_map", {})
            personas = project_data.get("personas", {})
            if not field_map or not personas:
                continue
                
            # Build mappings from slugified label to entry_id
            slug_to_entry = {}
            slug_letters_only = {}
            for entry_id, field_info in field_map.items():
                label = field_info.get("label", "")
                slug1 = re.sub(r'[^a-zA-Z0-9]', '', label).lower()[:20]
                slug2 = re.sub(r'[^a-z]', '', label.lower())[:20]
                if slug1:
                    slug_to_entry[slug1] = entry_id
                if slug2:
                    slug_letters_only[slug2] = entry_id
                    
            for persona_name, persona_config in personas.items():
                migrated_config = {}
                persona_changed = False
                for key, val in list(persona_config.items()):
                    if key.startswith("entry."):
                        migrated_config[key] = val
                    else:
                        target_key = slug_to_entry.get(key) or slug_letters_only.get(key)
                        if target_key:
                            migrated_config[target_key] = val
                            persona_changed = True
                        else:
                            migrated_config[key] = val
                if persona_changed:
                    project_data["personas"][persona_name] = migrated_config
                    migrated_any = True
        return migrated_any


    def save_all(self):
        with open(self.projects_file, 'w') as f:
            json.dump(self.projects, f, indent=4)
            
    def load_banned_emails(self):
        if os.path.exists(self.banned_emails_file):
            with open(self.banned_emails_file, 'r') as f:
                self.banned_emails = set(json.load(f))
        else:
            self.banned_emails = set()
            self.save_banned_emails()
            
    def save_banned_emails(self):
        with open(self.banned_emails_file, 'w') as f:
            json.dump(list(self.banned_emails), f, indent=4)
            
    def ban_email(self, email):
        self.banned_emails.add(email.lower().strip())
        self.save_banned_emails()
        
    def unban_email(self, email):
        email_clean = email.lower().strip()
        if email_clean in self.banned_emails:
            self.banned_emails.remove(email_clean)
            self.save_banned_emails()

    def parse_cookie_string(self, cookie_string):
        cookies = {}
        if not cookie_string:
            return cookies
        for item in cookie_string.split(';'):
            item = item.strip()
            if '=' in item:
                k, v = item.split('=', 1)
                cookies[k.strip()] = v.strip()
        return cookies

    def sanitize_url(self, url):
        parsed = urlparse(url)
        path = parsed.path
        if 'docs.google.com/forms' in url:
            if path.endswith('/edit') or path.endswith('/prefill'):
                path = path.replace('/edit', '/viewform').replace('/prefill', '/viewform')
            elif not path.endswith('/viewform') and not path.endswith('/formResponse'):
                if path.endswith('/'):
                    path += 'viewform'
                else:
                    path += '/viewform'
        return urlunparse((parsed.scheme, parsed.netloc, path, '', '', ''))

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

    def scrape_form(self, project_name, url, cookie_string="", user_agent=""):
        try:
            cookies = self.parse_cookie_string(cookie_string) if cookie_string else {}
            headers = {}
            if user_agent:
                headers["User-Agent"] = user_agent
            else:
                headers["User-Agent"] = random.choice(self.user_agents)

            # First, just get the URL to resolve any redirects (like forms.gle)
            response = self.session.get(url, headers=headers, cookies=cookies)
            
            # Now sanitize the final resolved URL
            clean_url = self.sanitize_url(response.url)
            
            # If the sanitized URL changed (e.g. added /viewform), we should fetch again
            if clean_url != response.url:
                response = self.session.get(clean_url, headers=headers, cookies=cookies)
            
            # More robust data extraction
            match = re.search(r'FB_PUBLIC_LOAD_DATA_ = (.*?);', response.text, re.DOTALL)
            if not match: 
                if '/d/e/' not in clean_url:
                    return False, "Could not find form data. Please ensure you are using the public 'viewform' link (from the Send button), not the edit link."
                return False, "Could not find FB_PUBLIC_LOAD_DATA. Form might be private or invalid."
            
            data = json.loads(match.group(1))
            
            # Recursive search for the questions array
            # A valid questions array is a list of lists, where each inner list has >= 4 elements:
            # item[0] is int (id), item[1] is string (title), item[3] is int (type)
            def find_questions(node):
                if isinstance(node, list):
                    # check if node is the questions array
                    if len(node) > 0 and isinstance(node[0], list) and len(node[0]) >= 4:
                        try:
                            if isinstance(node[0][0], int) and isinstance(node[0][1], str) and isinstance(node[0][3], int):
                                return node
                        except: pass
                    # recurse
                    for child in node:
                        res = find_questions(child)
                        if res: return res
                return None

            questions = find_questions(data)
            
            if not questions:
                return False, "Found form data but could not locate the questions array. Form structure might be unsupported."

            # Page Count detection
            pages_match = re.search(r'\[\[\d+,null,null,null,(\d+)\]', response.text)
            pages = int(pages_match.group(1)) if pages_match else 0
            
            field_map = {}
            for q in questions:
                try:
                    if not isinstance(q, list) or len(q) < 5 or q[4] is None:
                        continue
                        
                    label = q[1]
                    q_type = q[3] # 0: short, 1: para, 2: radio, 3: dropdown, 4: checkbox, 5: scale, 7: grid
                    
                    # Handle Grid questions (Type 7) which have nested rows
                    if q_type == 7:
                        # q[4][0] is usually a list of rows
                        if isinstance(q[4][0], list):
                            for row in q[4][0]:
                                if isinstance(row, list) and len(row) > 0:
                                    entry_id = row[0]
                                    row_label = f"{label} [{row[3][0]}]" if len(row) > 3 and row[3] else label
                                    
                                    # Extract columns as options from q[4][1]
                                    options = []
                                    if len(q[4]) > 1 and isinstance(q[4][1], list):
                                        options = [col[0] for col in q[4][1] if isinstance(col, list) and len(col) > 0]
                                        
                                    key = f"entry.{entry_id}"
                                    field_map[key] = {"label": row_label, "options": options, "required": False}
                        continue
                    
                    # Standard questions
                    entry_id = q[4][0][0]
                    required = q[4][0][2] if len(q[4][0]) > 2 else False
                    
                    options = []
                    # Check multiple locations for options (Radio/Checkbox)
                    if len(q[4][0]) > 1 and q[4][0][1]:
                        options = [opt[0] for opt in q[4][0][1] if isinstance(opt, list) and len(opt) > 0]
                    # Check for Linear Scale
                    elif len(q[4][0]) > 3 and q[4][0][3]:
                        options = [str(i) for i in range(1, 6)]
                    
                    key = f"entry.{entry_id}"
                    field_map[key] = {"label": label, "options": options, "required": required}
                except Exception as e: 
                    # Optionally log e, but continue to not break the whole form
                    continue
            
            if not field_map:
                return False, "Scraped form successfully, but no compatible input fields were found. The form might be empty or using an unsupported layout."

            self.projects[project_name]["url"] = clean_url
            self.projects[project_name]["field_map"] = field_map
            self.projects[project_name]["pages"] = pages
            self.projects[project_name]["cookie_string"] = cookie_string
            self.projects[project_name]["user_agent"] = user_agent
            self.save_all()
            return True, field_map
        except Exception as e:
            return False, f"Scrape Error: {str(e)}"

    def parse_baseline_responses(self, file_content_bytes, file_name):
        text = ""
        try:
            text = file_content_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text = file_content_bytes.decode('latin-1')
            except Exception as e:
                return False, f"Encoding error: {str(e)}"
        
        responses = []
        if file_name.lower().endswith('.csv'):
            import csv
            import io
            f = io.StringIO(text.strip())
            reader = csv.reader(f)
            rows = list(reader)
            if not rows:
                return False, "CSV is empty"
            for row in rows:
                row_vals = [cell.strip() for cell in row if cell.strip()]
                if row_vals:
                    responses.append(" | ".join(row_vals))
        else: # txt
            lines = text.split('\n')
            responses = [line.strip() for line in lines if line.strip()]
            
        if len(responses) < 10:
            return False, f"Too few baseline responses: Found {len(responses)}, minimum required is 10."
            
        if len(responses) > 50:
            responses = responses[:50]
            
        return True, responses

    def save_receipt(self, student_email, file_name, file_bytes):
        import os
        import time
        os.makedirs("receipts", exist_ok=True)
        timestamp = int(time.time())
        clean_email = re.sub(r'[^a-zA-Z0-9@.]', '_', student_email)
        clean_filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', file_name)
        saved_name = f"{timestamp}_{clean_email}_{clean_filename}"
        saved_path = os.path.join("receipts", saved_name)
        with open(saved_path, 'wb') as f:
            f.write(file_bytes)
        return saved_path

    def save_persona(self, project_name, persona_name, response_mapping):
        self.projects[project_name]["personas"][persona_name] = response_mapping
        self.save_all()

    def generate_persona(self, project_name, persona_name, tier="Basic", baseline_responses=None, additional_context=""):
        proj = self.projects[project_name]
        field_map = proj["field_map"]
        persona_config = proj["personas"].get(persona_name, {})
        
        # Check if Gemini API key is available in st.secrets only if Premium is selected
        api_key = None
        if tier == "Premium":
            try:
                import streamlit as st
                api_key = st.secrets.get("GEMINI_API_KEY")
            except Exception:
                pass

        # If Premium tier and API key is available, use LLM to generate high-fidelity coherent responses
        if tier == "Premium" and api_key:
            questions_specs = []
            for entry_id, info in field_map.items():
                config = persona_config.get(entry_id, {})
                if not config.get("enabled", True):
                    continue
                spec = {
                    "key": entry_id,
                    "question": info["label"]
                }
                if info["options"]:
                    spec["options"] = info["options"]
                custom_values = config.get("values", [])
                if custom_values:
                    spec["allowed_custom_values"] = custom_values
                questions_specs.append(spec)

            if questions_specs:
                baseline_str = ""
                if baseline_responses:
                    baseline_str = "Here are some baseline real human responses to guide your textual responses:\n" + "\n".join([f"- {r}" for r in baseline_responses]) + "\n\n"
                
                context_str = ""
                if additional_context:
                    context_str = f"Additional study context/guidelines:\n{additional_context}\n\n"

                prompt = (
                    f"You are a survey participant acting as the persona group: \"{persona_name}\".\n"
                    "Your task is to generate realistic, high-fidelity, coherent answers to the following survey questions.\n"
                    "Ensure that all answers are logically aligned with each other and fit the specified persona name naturally.\n\n"
                    f"{context_str}"
                    f"{baseline_str}"
                    "Instructions:\n"
                    "1. For questions with 'options', you MUST select one option from the list.\n"
                    "2. For questions with 'allowed_custom_values', you should select one of these custom values if possible.\n"
                    "3. For text questions (no 'options' or 'allowed_custom_values'), write a realistic, short (1-3 sentences) response in the persona's voice, matching the style/tone of the baseline responses if provided.\n\n"
                    "Questions:\n"
                    f"{json.dumps(questions_specs, indent=2)}\n\n"
                    "Respond with a single JSON object mapping keys directly to your generated answer. "
                    "Do not include any markdown styling, backticks, or extra text. Format example:\n"
                    "{\n"
                    "  \"entry.12345\": \"selected option or text\"\n"
                    "}"
                )
                
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                    headers = {"Content-Type": "application/json"}
                    schema_properties = {}
                    key_map = {} # Maps safe key to original key
                    for spec in questions_specs:
                        safe_key = spec["key"].replace(".", "_")
                        schema_properties[safe_key] = {"type": "STRING"}
                        key_map[safe_key] = spec["key"]
                        
                    payload = {
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": 0.7, 
                            "maxOutputTokens": 1000,
                            "responseMimeType": "application/json",
                            "responseSchema": {
                                "type": "OBJECT",
                                "properties": schema_properties,
                                "required": list(schema_properties.keys())
                            }
                        }
                    }
                    res = requests.post(url, json=payload, headers=headers, timeout=10)
                    if res.status_code == 200:
                        res_json = res.json()
                        response_text = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                        
                        # Clean up markdown code blocks if the model wrapped it
                        if response_text.startswith("```"):
                            start = response_text.find("{")
                            end = response_text.rfind("}")
                            if start != -1 and end != -1:
                                response_text = response_text[start:end+1]
                        
                        ai_data = json.loads(response_text)
                        
                        persona_data = {}
                        for entry_id, info in field_map.items():
                            config = persona_config.get(entry_id, {})
                            if not config.get("enabled", True):
                                continue
                            
                            safe_key = entry_id.replace(".", "_")
                            val = ai_data.get(safe_key)
                            if val is None:
                                val = ai_data.get(entry_id)
                            
                            if val is not None:
                                # Self-healing validation for options
                                options = info["options"]
                                if options and str(val) not in options:
                                    # Fuzzy close matching
                                    matches = difflib.get_close_matches(str(val), options, n=1, cutoff=0.3)
                                    if matches:
                                        val = matches[0]
                                    else:
                                        val = random.choice(options)
                                persona_data[entry_id] = val
                            else:
                                # Fallback if specific entry is missing
                                persona_data[entry_id] = self._fallback_generate(info, config, tier=tier)
                        return persona_data
                except Exception as e:
                    # Fallback to local generation on API failure
                    pass

        # Default local/fallback generation if key is missing, API fails, or Basic tier is selected
        persona_data = {}
        for entry_id, info in field_map.items():
            config = persona_config.get(entry_id, {})
            if not config.get("enabled", True):
                continue
            persona_data[entry_id] = self._fallback_generate(info, config, tier=tier)
        return persona_data

    def _fallback_generate(self, info, config, tier="Basic"):
        label = info["label"].lower()
        options = info["options"]
        custom_values = config.get("values", [])
        
        if custom_values:
            return random.choice(custom_values)

        # If it is Basic Tier and there are no standard options, treat as open-ended and return empty
        if tier == "Basic" and not options:
            return ""
            
        if options:
            return random.choice(options)
        elif "email" in label:
            if tier == "Basic":
                return ""
            return f"tester_{random.randint(100, 999)}@gmail.com"
        else:
            if tier == "Basic":
                return ""
            return f"Insight {random.randint(10, 99)}"

    def submit(self, project_name, payload, headers):
        proj = self.projects.get(project_name)
        if not proj: return False, "Project not found", {}
        
        url = proj["url"]
        form_url = url.replace("/viewform", "/formResponse")
        pages = proj.get("pages", 0)
        page_history = ",".join([str(i) for i in range(pages + 1)])
        
        cookie_string = proj.get("cookie_string", "")
        user_agent = proj.get("user_agent", "")
        cookies = self.parse_cookie_string(cookie_string) if cookie_string else {}
        
        if user_agent:
            headers = headers.copy() if headers else {}
            headers["User-Agent"] = user_agent
            
        try:
            resp = self.session.get(url, headers=headers, cookies=cookies)
            fbzx_m = re.search(r'name="fbzx"\s+value="([^"]+)"', resp.text)
            if not fbzx_m: return False, "fbzx token missing. Google blocked the GET request.", {}
            fbzx = fbzx_m.group(1)
            
            form_payload = [("fvv", "1"), ("pageHistory", page_history), ("fbzx", fbzx)]
            for eid, val in payload.items():
                if isinstance(val, list):
                    for v in val: form_payload.append((eid, str(v)))
                else:
                    form_payload.append((eid, str(val)))
            
            post_headers = headers.copy() if headers else {}
            post_headers["Content-Type"] = "application/x-www-form-urlencoded"
            post_headers["Referer"] = url
            post_headers["Origin"] = "https://docs.google.com"
            post_headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
            post_headers["Accept-Language"] = "en-US,en;q=0.9"
            
            res = self.session.post(form_url, data=form_payload, headers=post_headers, cookies=cookies)
            
            if res.status_code == 200 and "recorded" in res.text.lower():
                return True, "Success", {}
            else:
                return False, f"Status {res.status_code}", {"payload": form_payload, "response": res.text[:500]}
        except Exception as e:
            return False, f"Exception: {str(e)}", {}
