from engine import RiggingEngine

engine = RiggingEngine()

# Test local generation
proj_name = "re:AI"
persona_name = "Young First-time Buyers"
# Ensure the project exists in our projects
if proj_name in engine.projects:
    print("Testing Basic tier local generation:")
    res_basic = engine.generate_persona(proj_name, persona_name, tier="Basic")
    print("Basic tier results for open-ended entry.1140764828:", repr(res_basic.get("entry.1140764828")))
    
    print("\nTesting Premium tier local generation (without API key fallback):")
    res_prem_fallback = engine.generate_persona(proj_name, persona_name, tier="Premium")
    print("Premium tier fallback results for open-ended entry.1140764828:", repr(res_prem_fallback.get("entry.1140764828")))
else:
    print("re:AI project not found.")
