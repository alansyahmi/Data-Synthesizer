import json
import os
from engine import RiggingEngine

engine = RiggingEngine()
# mock the field map
engine.projects["Test"] = {
    "url": "https://docs.google.com/forms/d/e/1FAIpQLScX_x/viewform",
    "field_map": {
        "entry.111": {"label": "What is your favorite color?", "options": ["Red", "Blue", "Green"], "required": True},
        "entry.222": {"label": "Why do you like it?", "options": [], "required": False}
    },
    "personas": {
        "Default": {
            "entry.111": {"enabled": True, "values": []},
            "entry.222": {"enabled": True, "values": []}
        }
    },
    "pages": 0
}
res = engine.generate_persona("Test", "Default", tier="Premium")
print("Response:", res)
