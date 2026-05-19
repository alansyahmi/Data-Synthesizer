import streamlit as st
import time
import random
import json
from engine import RiggingEngine

# Page Config
st.set_page_config(page_title="Data Synthesizer", page_icon="🏢", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    .question-box { background-color: #1e2130; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #3d445e; }
    .debug-box { background-color: #1a1a1a; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 0.8em; color: #00ff00; border: 1px solid #333; }
    .persona-tag { background-color: #ff4b4b; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.8em; margin-right: 5px; }
    .template-count { color: #888; font-size: 0.8em; }
    .status-card { background-color: #1e2130; padding: 12px; border-radius: 8px; margin-top: 15px; border: 1px solid #2d3142; }
    .status-badge-green { background-color: rgba(46, 204, 113, 0.15); color: #2ecc71; border: 1px solid #2ecc71; padding: 4px 10px; border-radius: 20px; font-size: 0.8em; font-weight: bold; display: inline-block; }
    .status-badge-yellow { background-color: rgba(241, 196, 15, 0.15); color: #f1c40f; border: 1px solid #f1c40f; padding: 4px 10px; border-radius: 20px; font-size: 0.8em; font-weight: bold; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

if 'engine' not in st.session_state:
    st.session_state.engine = RiggingEngine()

# SIDEBAR
with st.sidebar:
    st.title("🏢 Workspace")
    project_list = list(st.session_state.engine.projects.keys())
    active_project = st.selectbox("Select Active Project", project_list)
    
    st.markdown("---")
    with st.expander("➕ New Project"):
        new_proj_input = st.text_input("New Project Name", key="new_proj_input")
        if st.button("Create Project"):
            if new_proj_input:
                st.session_state.engine.create_project(new_proj_input)
                st.rerun()
                
    st.markdown("---")
    st.subheader("🤖 Engine Status")
    api_key_set = False
    try:
        api_key_set = "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    if api_key_set:
        st.markdown(
            '<div class="status-card">'
            '<div class="status-badge-green">🟢 High-Fidelity Active</div>'
            '<p style="font-size: 0.85em; color: #aaa; margin-top: 8px; margin-bottom: 0;">'
            'Gemini 1.5 Flash is powered via secure secrets. Generating highly context-aware persona data.</p>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="status-card">'
            '<div class="status-badge-yellow">🟡 Local Fallback Active</div>'
            '<p style="font-size: 0.85em; color: #aaa; margin-top: 8px; margin-bottom: 0;">'
            'No Gemini API Key detected in st.secrets. Operating in secure deterministic local mock mode.</p>'
            '</div>',
            unsafe_allow_html=True
        )

# MAIN
st.title(f"🚀 {active_project}")
current_proj = st.session_state.engine.projects[active_project]
tab_setup, tab_run, tab_lab = st.tabs(["⚙️ Setup", "⚡ Dispatcher", "🧪 Persona Lab"])

with tab_setup:
    st.header("Form Configuration")
    form_url = st.text_input("Google Form View URL", value=current_proj.get("url", ""), placeholder="https://docs.google.com/forms/d/e/...")
    if st.button("Analyze & Scrape Form"):
        if form_url:
            with st.spinner("Scraping metadata..."):
                success, result = st.session_state.engine.scrape_form(active_project, form_url)
                if success: st.rerun()
                else: st.error(result)

with tab_run:
    st.header("Synthetic Dispatch")
    if not current_proj.get("url") or not current_proj.get("field_map"):
        st.warning("⚠️ Please complete 'Setup' first.")
    elif not current_proj.get("personas"):
        st.warning("⚠️ Create persona groups in the 'Persona Lab' first.")
    else:
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            flavor = st.selectbox("Select Persona Group", list(current_proj["personas"].keys()))
            limit = st.slider("Submissions", 1, 100, 3)
        with col_s2:
            delay = st.slider("Min Delay (sec)", 1, 10, 3)
            
        if st.button("🚀 Execute Run"):
            progress = st.progress(0)
            status = st.empty()
            success_count = 0
            for i in range(limit):
                status.text(f"Running Persona {i+1}/{limit}...")
                persona = st.session_state.engine.generate_persona(active_project, flavor)
                headers = {"User-Agent": random.choice(st.session_state.engine.user_agents)}
                success, message, debug_info = st.session_state.engine.submit(active_project, persona, headers)
                if success:
                    success_count += 1
                else:
                    st.error(f"Failed: {message}")
                    if debug_info:
                        with st.expander("🔍 View Debug Payload"):
                            st.json(debug_info.get("payload"))
                            st.code(debug_info.get("response"))
                    break
                progress.progress((i + 1) / limit)
                time.sleep(random.uniform(delay, delay + 2))
            if success_count > 0:
                st.balloons()
                st.success(f"Successfully recorded {success_count} responses.")

with tab_lab:
    st.header("🧪 Persona Lab")
    if not current_proj.get("field_map"):
        st.warning("⚠️ Please scrape a form in 'Setup' before editing persona groups.")
    else:
        existing_personas = ["+ Create New Persona Group"] + list(current_proj["personas"].keys())
        p_to_edit = st.selectbox("Choose Persona Group to Edit", existing_personas)
        
        if p_to_edit == "+ Create New Persona Group":
            p_name = st.text_input("New Persona Name", key="new_p_name_input")
            edit_config = {}
        else:
            p_name = p_to_edit
            edit_config = current_proj["personas"][p_to_edit]

        if p_name:
            st.markdown("---")
            st.subheader(f"Editing: {p_name}")
            new_response_map = {}
            for entry_id, info in current_proj["field_map"].items():
                with st.container():
                    st.markdown(f'<div class="question-box">', unsafe_allow_html=True)
                    req_tag = '<span class="required-tag">(REQUIRED)</span>' if info.get("required") else ""
                    st.markdown(f'**{info["label"]}** {req_tag}', unsafe_allow_html=True)
                    is_req = info.get("required")
                    q_enabled = st.toggle("Include in persona?", value=edit_config.get(entry_id, {}).get("enabled", True) if not is_req else True, disabled=is_req, key=f"en_{entry_id}_{p_name}")
                    
                    if q_enabled:
                        if info["options"]:
                            selected_vals = st.multiselect("Select valid options", info["options"], default=edit_config.get(entry_id, {}).get("values", []), key=f"val_{entry_id}_{p_name}")
                            new_response_map[entry_id] = {"enabled": True, "values": selected_vals}
                        else:
                            existing_vals = edit_config.get(entry_id, {}).get("values", [])
                            existing_text = "\n".join(existing_vals)
                            st.markdown(f'<span class="template-count">{len(existing_vals)} templates found</span>', unsafe_allow_html=True)
                            text_templates = st.text_area("Response Templates (Put each variation on a new line)", 
                                                         value=existing_text, 
                                                         placeholder="Example:\nI love this product\nI highly recommend it!",
                                                         key=f"txt_{entry_id}_{p_name}",
                                                         height=100)
                            new_response_map[entry_id] = {"enabled": True, "values": [t.strip() for t in text_templates.split("\n") if t.strip()]}
                    else:
                        new_response_map[entry_id] = {"enabled": False, "values": []}
                    st.markdown('</div>', unsafe_allow_html=True)

            if st.button("💾 Save Persona Group Configuration"):
                if p_name and p_name != "+ Create New Persona Group":
                    st.session_state.engine.save_persona(active_project, p_name, new_response_map)
                    st.success(f"Persona Group '{p_name}' saved!")
                    st.rerun()

st.markdown("---")
st.caption("Developed for Technopreneurship | UMS")
