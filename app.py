import streamlit as st
import time
import random
import json
from engine import RiggingEngine

# Page Config
st.set_page_config(page_title="Synthify", page_icon="◎", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kodchasan:wght@400;600;700&family=Kulim+Park:wght@400;600;700&display=swap');

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes underlineSweep {
        from { transform: scaleX(0); transform-origin: left; }
        to { transform: scaleX(1); transform-origin: left; }
    }

    /* Clean base */
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(255, 193, 7, 0.08), transparent 24%),
            radial-gradient(circle at top right, rgba(17, 17, 17, 0.05), transparent 18%),
            linear-gradient(180deg, #FAFAFA 0%, #F7F7F4 100%);
        font-family: 'Kulim Park', sans-serif;
        color: #333333;
    }
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .main-shell { animation: fadeInUp 0.45s ease both; }
    .hero-panel { animation: fadeInUp 0.55s ease both; }
    .hero-panel p { animation: fadeInUp 0.7s ease both; }
    .section-block { animation: fadeInUp 0.35s ease both; }
    .footer-shell { opacity: 0.92; }
    .feedback-card {
        background: linear-gradient(180deg, #FFFFFF 0%, #FCFCFA 100%);
        border: 1px solid #EAEAEA;
        border-left-width: 4px;
        border-radius: 10px;
        padding: 14px 16px;
        margin: 10px 0 18px 0;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.04);
        animation: fadeInUp 0.35s ease both;
    }
    @keyframes pulseSuccess {
        0% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(46, 204, 113, 0); }
        100% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0); }
    }
    .feedback-card.success { 
        border-left-width: 6px;
        border-left-color: #2ECC71; 
        background: linear-gradient(135deg, #F0FFF4 0%, #FFFFFF 100%);
        animation: fadeInUp 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) both, pulseSuccess 2s infinite;
        border: 1px solid #C6F6D5;
        border-left: 6px solid #2ECC71;
    }
    .feedback-card.warning { border-left-color: #FFC107; }
    .feedback-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'Kodchasan', sans-serif;
        font-weight: 700;
        color: #111111;
        margin-bottom: 4px;
    }
    .feedback-body {
        color: #666666;
        font-size: 0.95rem;
        line-height: 1.45;
    }
    .feedback-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
    }
    .feedback-chip {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 0.25rem 0.7rem;
        background: #F5F5F5;
        color: #444444;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.01em;
    }
    
    /* Hide default streamlit decorations */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Typography & Core UI */
    h1, h2, h3 { color: #111111 !important; font-family: 'Kodchasan', sans-serif; font-weight: 600; }
    p, span, div { font-family: 'Kulim Park', sans-serif; }
    
    /* SYNTHIFY_OS Header accent */
    .synth-accent { color: #FFC107; font-weight: 700; }
    .synth-header { font-size: 2.5rem; line-height: 1.2; margin-bottom: 0.5rem; font-family: 'Kodchasan', sans-serif; font-weight: 700; letter-spacing: -0.02em; }
    .hero-tagline { display: inline-block; color: #111111; font-family: 'Kodchasan', sans-serif; font-weight: 700; letter-spacing: -0.02em; }
    .hero-tagline::after {
        content: "";
        display: block;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #FFC107, rgba(255, 193, 7, 0.15));
        margin-top: 0.35rem;
        animation: underlineSweep 0.8s ease both;
    }
    /* Buttons reverted to Streamlit default */
    /* Input Fields */
    .stTextInput>div>div>input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div,
    .stRadio [role="radiogroup"] label {
        transition: border-color 160ms ease, box-shadow 160ms ease, transform 160ms ease, background-color 160ms ease;
    }
    .stTextInput>div>div>input {
        border-radius: 4px;
        border: 1px solid #E0E0E0;
        background-color: #FFFFFF;
        color: #333333;
        padding: 10px 15px;
    }
    .stTextInput>div>div>input:focus,
    .stTextArea textarea:focus,
    .stSelectbox div[data-baseweb="select"] > div:focus-within {
        border: 1px solid #FFC107;
        box-shadow: 0 0 0 2px rgba(255, 193, 7, 0.16);
        transform: translateY(-1px);
    }

    /* Custom classes */
    .question-box {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 1px solid #EEEEEE;
        border-top: 4px solid #FFC107;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
    }
    .question-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(0,0,0,0.07);
        border-color: #E2E2E2;
    }
    .schema-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 1px solid #EAEAEA;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        display: flex;
        flex-direction: column;
        transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
    }
    .schema-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 24px rgba(0,0,0,0.07);
        border-color: #D8D8D8;
    }
    .schema-icon { background-color: #F5F5F5; border-radius: 4px; padding: 10px; width: fit-content; margin-bottom: 15px; }
    .schema-tag { background-color: #FFF8E1; color: #B9860B; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; align-self: flex-end; }
    .schema-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 5px; font-family: 'Kodchasan', sans-serif; }
    .schema-subtitle { font-size: 0.8rem; color: #888888; margin-bottom: 15px; }
    .schema-footer { background-color: #F9F9F9; padding: 8px 12px; border-radius: 4px; font-size: 0.8rem; display: flex; align-items: center; }
    .schema-dot { height: 8px; width: 8px; background-color: #2ECC71; border-radius: 50%; display: inline-block; margin-right: 8px; }

    .debug-box { background-color: #F8F9FA; padding: 15px; border-radius: 4px; font-family: monospace; font-size: 0.8em; color: #333333; border: 1px solid #E9ECEF; }
    .persona-tag { background-color: #FFC107; color: #000000; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; margin-right: 5px; font-weight: bold; }
    .template-count { color: #888888; font-size: 0.8em; }
    
    /* Tabs Customization */
    button[role="tab"] {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        padding: 10px 25px !important;
        font-family: 'Kodchasan', sans-serif !important;
    }
    div[role="tablist"] {
        justify-content: center !important;
        gap: 20px !important;
    }
    div[data-testid="stRadio"] > div {
        flex-direction: row !important;
        justify-content: center !important;
        gap: 0.65rem !important;
    }
    div[data-testid="stRadio"] label {
        background: #FFFFFF !important;
        border: 1px solid #EAEAEA !important;
        border-radius: 999px !important;
        padding: 0.45rem 1rem !important;
        font-family: 'Kodchasan', sans-serif !important;
        font-weight: 700 !important;
        color: #111111 !important;
        margin: 0 !important;
    }
    div[data-testid="stRadio"] label:hover {
        border-color: #FFC107 !important;
        transform: translateY(-1px);
    }
    div[data-testid="stRadio"] label[data-checked="true"] {
        background: #111111 !important;
        color: #FFFFFF !important;
        border-color: #111111 !important;
    }
    
    /* Dividers */
    hr { border-top: 1px solid #EAEAEA; margin: 0.9rem 0 1.2rem; }

    /* Primary action styling */
    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #111111;
        color: #FFFFFF;
        border: 1px solid #111111;
        transition: transform 160ms ease, box-shadow 160ms ease, background-color 160ms ease, border-color 160ms ease;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background-color: #FFC107;
        color: #111111;
        border-color: #FFC107;
        transform: translateY(-1px);
        box-shadow: 0 8px 18px rgba(255, 193, 7, 0.18);
    }
    div[data-testid="stButton"] > button[kind="secondary"] {
        background: transparent !important;
        color: #111111 !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        min-height: 0 !important;
        margin-left: auto !important;
        display: block !important;
        width: fit-content !important;
        font-family: 'Kulim Park', sans-serif !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        text-decoration: none !important;
        transition: color 160ms ease, transform 160ms ease, text-decoration-color 160ms ease;
    }
    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        background: transparent !important;
        color: #111111 !important;
        border: none !important;
        text-decoration: underline !important;
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)

if 'engine' not in st.session_state:
    st.session_state.engine = RiggingEngine()

if 'uploader_id' not in st.session_state:
    st.session_state.uploader_id = 0

if 'show_admin_panel' not in st.session_state:
    st.session_state.show_admin_panel = False

if 'active_section' not in st.session_state:
    st.session_state.active_section = "01 SETUP"


def open_admin_panel():
    st.session_state.show_admin_panel = True


def open_workspace():
    st.session_state.active_section = "01 SETUP"
    st.session_state.show_admin_panel = False


def open_section(section_name: str):
    st.session_state.active_section = section_name
    st.session_state.show_admin_panel = False


def sync_active_section():
    st.session_state.active_section = st.session_state.step_selector
    st.session_state.show_admin_panel = False


def celebrate(title, body, kind="success"):
    icon = "◎" if kind == "success" else "☍"
    css_kind = "success" if kind == "success" else "warning"
    
    if kind == "success":
        st.balloons()
        
    st.markdown(
        f"""
        <div class="feedback-card {css_kind}">
            <div class="feedback-title"><span style="font-size: 1.2em; margin-right: 4px; display: inline-block; animation: bounceIcon 2s infinite;">{icon}</span> {title}</div>
            <div class="feedback-body">{body}</div>
        </div>
        <style>
        @keyframes bounceIcon {{
            0%, 20%, 50%, 80%, 100% {{transform: translateY(0);}}
            40% {{transform: translateY(-4px);}}
            60% {{transform: translateY(-2px);}}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def queue_feedback(title, body, kind="success"):
    st.session_state.pending_feedback = {"title": title, "body": body, "kind": kind}


def render_admin_panel():
    st.markdown('<div class="section-block" style="font-size: 1.3rem; font-family: \'Kodchasan\', sans-serif; font-weight: 600; border-bottom: 2px solid #FFC107; display: inline-block; padding-bottom: 5px; margin-bottom: 20px;">◎ Admin Panel</div>', unsafe_allow_html=True)
    st.button("Back to Workspace", key="admin_back_button", on_click=open_workspace)

    correct_pass = None
    try:
        correct_pass = st.secrets.get("ADMIN_PASSWORD")
    except Exception:
        pass

    if not correct_pass:
        st.warning("◎ Admin Password is not configured. Please add `ADMIN_PASSWORD = \"yourpassword\"` to `.streamlit/secrets.toml` to access this panel.")
        return

    admin_pass_input = st.text_input("Enter Admin Password", type="password", key="admin_password_input_field")
    if admin_pass_input == correct_pass:
        st.success("◎ Access Granted.")
        st.markdown('<div style="font-size: 1.1rem; font-family: \'Kodchasan\', sans-serif; font-weight: 600; margin-top: 20px; margin-bottom: 10px;">◎ Transaction Logs & Receipts</div>', unsafe_allow_html=True)

        import os
        import datetime

        if not os.path.exists("receipts") or not os.listdir("receipts"):
            st.info("No transaction receipts uploaded yet.")
        else:
            files = os.listdir("receipts")
            logs = []
            for idx, fname in enumerate(files):
                parts = fname.split('_', 2)
                if len(parts) == 3:
                    tstamp, email, orig_name = parts
                    try:
                        date_str = datetime.datetime.fromtimestamp(int(tstamp)).strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        date_str = "Unknown"
                else:
                    date_str = "Unknown"
                    email = "Unknown"
                    orig_name = fname

                logs.append({
                    "No": idx + 1,
                    "Timestamp": date_str,
                    "Student Email": email,
                    "File Name": orig_name,
                    "System Path": os.path.join("receipts", fname)
                })

            st.markdown("| No | Timestamp | Student Email | File Name |")
            st.markdown("| --- | --- | --- | --- |")
            for log in logs:
                st.markdown(f"| {log['No']} | {log['Timestamp']} | {log['Student Email']} | {log['File Name']} |")

            st.markdown("---")
            st.subheader("◎ Receipt File Viewer")
            selected_log_idx = st.selectbox(
                "Select Receipt to Inspect",
                options=range(len(logs)),
                format_func=lambda i: f"#{i+1} - {logs[i]['Student Email']} ({logs[i]['Timestamp']})"
            )

            selected_log = logs[selected_log_idx]
            r_path = selected_log["System Path"]

            if os.path.exists(r_path):
                with open(r_path, "rb") as f:
                    file_bytes = f.read()

                file_ext = selected_log["File Name"].split('.')[-1].lower()
                if file_ext in ["png", "jpg", "jpeg"]:
                    try:
                        st.image(file_bytes, caption=f"Receipt from {selected_log['Student Email']}", width=450)
                    except Exception:
                        st.warning("◎ Could not render receipt image preview. File may be corrupted or contains invalid image data.")
                else:
                    st.info("◎ PDF or Binary file receipt. Click below to download and inspect.")

                st.download_button(
                    label=f"Download {selected_log['File Name']}",
                    data=file_bytes,
                    file_name=selected_log["File Name"],
                    mime="application/octet-stream"
                )

# MAIN
st.markdown(
    f"""
    <div class="main-shell" style="display: flex; justify-content: flex-start; align-items: center; border-bottom: 1px solid #EAEAEA; padding-bottom: 10px; margin-bottom: 18px;">
        <div style="font-family: 'Kodchasan', sans-serif; font-size: 1.5rem; font-weight: 700; color: #FFC107;">SYNTHIFY</div>
    </div>
    """,
    unsafe_allow_html=True
)

hero_col1, hero_col2 = st.columns([2, 1])

with hero_col1:
    st.markdown(
        """
        <div class="hero-panel">
            <div class="synth-header"><span class="hero-tagline">Scrape, Personalize, Dispatch</span></div>
            <p style="color: #666; font-size: 1.1rem; max-width: 600px; margin-bottom: 0;">Synthify helps you capture Google Form structure, organize response templates, and run guided synthetic dispatch from one clean workspace.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with hero_col2:
    project_list = list(st.session_state.engine.projects.keys())
    active_project = st.selectbox("Select Active Project", project_list, label_visibility="collapsed")
    
    with st.expander("+ New Project"):
        new_proj_input = st.text_input("New Project Name", key="new_proj_input", label_visibility="collapsed", placeholder="New Project Name")
        if st.button("+ Create Project"):
            if new_proj_input:
                st.session_state.engine.create_project(new_proj_input)
                st.rerun()
                
    api_key_set = False
    try:
        api_key_set = "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    if api_key_set:
        st.markdown(
            '<div style="font-size: 0.75rem; color: #2ecc71; margin-top: 10px; font-weight: bold;">◎ High-Fidelity Active</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div style="font-size: 0.75rem; color: #f39c12; margin-top: 10px; font-weight: bold;">◎ Local Fallback Active</div>',
            unsafe_allow_html=True
        )

current_proj = st.session_state.engine.projects[active_project]
step_bar = st.radio(
    label="Workspace Steps",
    options=["01 SETUP", "02 PERSONA", "03 DISPATCH"],
    index=["01 SETUP", "02 PERSONA", "03 DISPATCH"].index(st.session_state.active_section)
    if st.session_state.active_section in ["01 SETUP", "02 PERSONA", "03 DISPATCH"]
    else 0,
    horizontal=True,
    label_visibility="collapsed",
    key="step_selector",
    on_change=sync_active_section,
)

if st.session_state.show_admin_panel:
    render_admin_panel()
elif step_bar == "01 SETUP":
    pending_feedback = st.session_state.pop("pending_feedback", None)
    if pending_feedback:
        celebrate(pending_feedback["title"], pending_feedback["body"], pending_feedback["kind"])
    st.markdown('<div class="section-block" style="font-size: 1.3rem; font-family: \'Kodchasan\', sans-serif; font-weight: 600; border-bottom: 2px solid #FFC107; display: inline-block; padding-bottom: 5px; margin-bottom: 20px;">◎ Target Acquisition</div>', unsafe_allow_html=True)
            
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        form_url = st.text_input("Insert Google Form URL for extraction...", value=current_proj.get("url", ""), label_visibility="collapsed", placeholder="Insert Google Form URL for extraction...")
    with col_btn:
        if st.button("SCRAPE FORM ➔", type="primary", use_container_width=True):
            if form_url:
                with st.spinner("Scraping metadata..."):
                    success, result = st.session_state.engine.scrape_form(active_project, form_url)
                    if success:
                        field_count = len(result)
                        page_count = st.session_state.engine.projects[active_project].get("pages", 0)
                        queue_feedback(
                            "Form mapped",
                            f"Detected {field_count} fields and unlocked the Persona Lab" + (f" across {page_count} page(s)." if page_count else "."),
                            "success",
                        )
                        st.toast(f"Mapped {field_count} fields. Persona Lab is ready.")
                        st.rerun()
                    else: 
                        st.error(result)
                                
    if current_proj.get("field_map"):
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div style="font-size: 1.3rem; font-family: \'Kodchasan\', sans-serif; font-weight: 600; margin-bottom: 5px;">☍ Detected Fields</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.85rem; color: #888; margin-bottom: 20px;">These form fields were successfully detected and are ready to be configured.</div>', unsafe_allow_html=True)
                
        fields = list(current_proj["field_map"].items())
        for i in range(0, len(fields), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(fields):
                    k, v = fields[i + j]
                    with cols[j]:
                        type_str = "Open-ended" if not v.get("options") else "Multiple Choice"
                        opt_count = f"{len(v['options'])} Available Options" if v.get("options") else "Requires text input"
                                
                        options_html = ""
                        if v.get("options"):
                            opts = ", ".join(v["options"])
                            if len(opts) > 100: opts = opts[:97] + "..."
                            options_html = f'<div style="font-size: 0.75rem; color: #555; margin-bottom: 15px; background-color: #F8F9FA; padding: 8px; border-radius: 4px; border: 1px solid #EAEAEA;">{opts}</div>'
                        else:
                            options_html = f'<div style="font-size: 0.75rem; color: #888; margin-bottom: 15px; background-color: #F8F9FA; padding: 8px; border-radius: 4px; border: 1px dashed #EAEAEA; font-style: italic;">Open-ended response</div>'
                        st.markdown(f"""
                        <div class="schema-card">
                            <div style="display: flex; justify-content: space-between;">
                                <div class="schema-icon">⊞</div>
                                <div class="schema-tag">{type_str}</div>
                            </div>
                            <div class="schema-title">{v['label']}</div>
                            <div class="schema-subtitle">Question ID: {k}</div>
                            {options_html}
                            <div class="schema-footer">
                                <span class="schema-dot"></span> {opt_count}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

elif step_bar == "03 DISPATCH":
    pending_feedback = st.session_state.pop("pending_feedback", None)
    if pending_feedback:
        celebrate(pending_feedback["title"], pending_feedback["body"], pending_feedback["kind"])
    st.markdown('<div class="section-block" style="font-size: 1.3rem; font-family: \'Kodchasan\', sans-serif; font-weight: 600; border-bottom: 2px solid #FFC107; display: inline-block; padding-bottom: 5px; margin-bottom: 20px;">↗ Synthetic Dispatch</div>', unsafe_allow_html=True)
    if not current_proj.get("url") or not current_proj.get("field_map"):
        st.warning("◎ Please complete 'Setup' first.")
    elif not current_proj.get("personas"):
        st.warning("◎ Create persona groups in the 'Persona Lab' first.")
    else:
        # Enforce UMS student email validation (Accountability Gate)
        st.markdown('<div style="font-size: 1.1rem; font-family: \'Kodchasan\', sans-serif; font-weight: 600; margin-top: 20px; margin-bottom: 10px;">▸ 1. Accountability Gate</div>', unsafe_allow_html=True)
        student_email = st.text_input(
            "Enter your official UMS Email Address (@student.ums.edu.my or @ums.edu.my)", 
            placeholder="e.g. name@student.ums.edu.my",
            key=f"email_input_{st.session_state.uploader_id}"
        )
        email_valid = False
        if student_email:
            if "ums.edu.my" in student_email.lower().strip():
                st.success("◎ Email verified: Official UMS domain.")
                email_valid = True
            else:
                st.error("☍ Email invalid: Must be a UMS domain (containing 'ums.edu.my').")
        else:
            st.info("◎ Please enter your student email to proceed.")

        st.markdown("---")

        # Tier Selector Toggles
        st.markdown('<div style="font-size: 1.1rem; font-family: \'Kodchasan\', sans-serif; font-weight: 600; margin-top: 20px; margin-bottom: 10px;">▸ 2. Tier Selection</div>', unsafe_allow_html=True)
        tier = st.radio(
            "Choose execution tier:",
            options=["Basic Tier (RM1.50) - Quantitative Only", "Premium Tier (RM3.00) - Context Answers (Requires Gemini AI)"],
            help="Basic Tier only fills quantitative fields (radio buttons, ratings, scale, checkbox). Premium Tier uses Gemini AI to generate realistic open-ended responses."
        )
        is_premium = "Premium" in tier
        selected_tier = "Premium" if is_premium else "Basic"

        st.markdown("---")

        # Context & Baseline Uploader (Premium Only)
        baseline_responses = None
        study_context = ""
        baseline_valid = True
                
        if is_premium:
            st.markdown('<div style="font-size: 1.1rem; font-family: \'Kodchasan\', sans-serif; font-weight: 600; margin-top: 20px; margin-bottom: 10px;">▸ 3. Context & Human Baselines</div>', unsafe_allow_html=True)
            study_context = st.text_area(
                "Study Context / Guidelines", 
                placeholder="Describe your research topic, context, or guidelines (e.g., 'A study on UMS student transport challenges and campus shuttle bus arrival delay stress...')"
            )
                    
            baseline_file = st.file_uploader(
                "Upload Baseline Real Human Responses (.txt or .csv)",
                type=["txt", "csv"],
                help="Provide a text file (one response per line) or a CSV file containing 10 to 50 real responses to guide open-ended generation.",
                key=f"baseline_uploader_{st.session_state.uploader_id}"
            )
                    
            # Baseline templates for QoL downloads
            txt_template = (
                "Sangat lambat, bas selalu lambat sampai ke perhentian.\n"
                "Bas tidak cukup, terpaksa beratur panjang setiap pagi.\n"
                "Shuttle bus UMS kurang selesa dan tiada aircond.\n"
                "Pemandu bas memandu secara berbahaya kerana kejar masa.\n"
                "Kawasan menunggu bas terlalu panas dan tiada teduhan.\n"
                "Laluan bas UMS tidak efisien, membuang masa pelajar.\n"
                "Kekerapan bas pada waktu puncak amat mengecewakan.\n"
                "Pernah terlewat menduduki peperiksaan sebab bas rosak.\n"
                "Tambang bas kampus patut dimansuhkan terus.\n"
                "Sistem penjejakan GPS bas tidak berfungsi dengan baik."
            )
            csv_template = (
                "response\n"
                "\"Sangat lambat, bas selalu lambat sampai ke perhentian.\"\n"
                "\"Bas tidak cukup, terpaksa beratur panjang setiap pagi.\"\n"
                "\"Shuttle bus UMS kurang selesa dan tiada aircond.\"\n"
                "\"Pemandu bas memandu secara berbahaya kerana kejar masa.\"\n"
                "\"Kawasan menunggu bas terlalu panas dan tiada teduhan.\"\n"
                "\"Laluan bas UMS tidak efisien, membuang masa pelajar.\"\n"
                "\"Kekerapan bas pada waktu puncak amat mengecewakan.\"\n"
                "\"Pernah terlewat menduduki peperiksaan sebab bas rosak.\"\n"
                "\"Tambang bas kampus patut dimansuhkan terus.\"\n"
                "\"Sistem penjejakan GPS bas tidak berfungsi dengan baik.\""
            )
                    
            with st.expander("⊞ Get Sample Baseline Templates"):
                st.write("Use these templates to check correct baseline upload formatting:")
                d_col1, d_col2 = st.columns(2)
                with d_col1:
                    st.download_button(
                        label="Download TXT Template",
                        data=txt_template,
                        file_name="ums_baseline_template.txt",
                        mime="text/plain"
                    )
                with d_col2:
                    st.download_button(
                        label="Download CSV Template",
                        data=csv_template,
                        file_name="ums_baseline_template.csv",
                        mime="text/csv"
                    )

            if baseline_file:
                success, parsed_res = st.session_state.engine.parse_baseline_responses(baseline_file.read(), baseline_file.name)
                if success:
                    baseline_responses = parsed_res
                    st.success(f"◎ Baseline parsed successfully! Found {len(baseline_responses)} human responses.")
                    with st.expander("⊞ Preview Baseline Data"):
                        st.write(baseline_responses)
                else:
                    st.error(f"☍ Error: {parsed_res}")
                    baseline_valid = False
            else:
                st.warning("◎ Human baseline responses are required for Premium Tier context-aware generation (Minimum 10).")
                baseline_valid = False
                        
            st.markdown("---")

        # Dispatch Configuration
        st.markdown('<div style="font-size: 1.1rem; font-family: \'Kodchasan\', sans-serif; font-weight: 600; margin-top: 20px; margin-bottom: 10px;">▸ 4. Run Configuration</div>', unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            flavor = st.selectbox("Select Persona Group", list(current_proj["personas"].keys()))
            limit = st.slider("Submissions (Max 50 per transaction)", 1, 50, 3)
        with col_s2:
            delay = st.slider("Min Delay (sec)", 1, 10, 3)

        st.markdown("---")

        # Payment Interface Box
        st.markdown('<div style="font-size: 1.1rem; font-family: \'Kodchasan\', sans-serif; font-weight: 600; margin-top: 20px; margin-bottom: 10px;">▸ 5. Payment Verification</div>', unsafe_allow_html=True)
        st.write("Scan the DuitNow QR code below to complete the transaction.")
                
        pay_col1, pay_col2 = st.columns([1, 1.5])
        with pay_col1:
            import os
            if os.path.exists("duitnow_qr_code.png"):
                st.image("duitnow_qr_code.png", caption="Thanks for using our service!", width=260)
            else:
                st.error("QR Code asset missing from workspace!")
                
        with pay_col2:
            price = "RM3.00" if is_premium else "RM1.50"
            st.markdown(f"#### Amount Due: **{price}**")
            st.markdown(
                "1. Scan the QR code on the left to make your payment.\n"
                "2. Upload a screenshot or PDF of the receipt/transaction below.\n"
                "3. Once the receipt is uploaded, the execution button will unlock."
            )
            receipt_file = st.file_uploader(
                "Upload Payment Receipt screenshot/file", 
                type=["png", "jpg", "jpeg", "pdf"],
                key=f"receipt_uploader_{st.session_state.uploader_id}"
            )
            if receipt_file:
                file_extension = receipt_file.name.split('.')[-1].lower()
                if file_extension in ["png", "jpg", "jpeg"]:
                    try:
                        st.image(receipt_file, caption="Receipt Preview", width=220)
                    except Exception:
                        st.warning("◎ Could not render receipt image preview. The uploaded file contains invalid image data.")
                else:
                    st.success(f"◎ Receipt file '{receipt_file.name}' ready.")

        st.markdown("---")

        # Submission Check
        ready_to_submit = False
        if email_valid and receipt_file:
            if not is_premium or (is_premium and baseline_valid):
                ready_to_submit = True
                        
        # Main execution button locked until conditions are met
        if not ready_to_submit:
            st.info("↗ The dispatch button is locked. Please enter a valid UMS email, configure necessary baseline data (Premium only), and upload your transaction receipt.")
                    
        # Action Buttons Layout
        btn_col1, btn_col2 = st.columns([4, 1])
        with btn_col1:
            execute_button = st.button(
                "▸ Execute Run", 
                disabled=not ready_to_submit,
                help="Unlocks after email validation, human baseline upload (for Premium), and receipt verification."
            )
        with btn_col2:
            if st.button("⊞ Clear Form State"):
                st.session_state.uploader_id += 1
                st.rerun()

        success_count = 0
        if execute_button:
            # First, save receipt
            receipt_bytes = receipt_file.getvalue()
            saved_path = st.session_state.engine.save_receipt(student_email, receipt_file.name, receipt_bytes)
            st.info(f"◎ Receipt saved successfully to: `{saved_path}`")
                    
            # Start run
            progress = st.progress(0)
            status = st.empty()
            success_count = 0
            for i in range(limit):
                status.text(f"Running Persona {i+1}/{limit}...")
                        
                # Pass Premium context parameters
                persona = st.session_state.engine.generate_persona(
                    active_project, 
                    flavor,
                    tier=selected_tier,
                    baseline_responses=baseline_responses,
                    additional_context=study_context
                )
                        
                headers = {"User-Agent": random.choice(st.session_state.engine.user_agents)}
                success, message, debug_info = st.session_state.engine.submit(active_project, persona, headers)
                if success:
                    success_count += 1
                else:
                    st.error(f"Failed: {message}")
                    if debug_info:
                        with st.expander("⊞ View Debug Payload"):
                            st.json(debug_info.get("payload"))
                            st.code(debug_info.get("response"))
                    break
                progress.progress((i + 1) / limit)
                time.sleep(random.uniform(delay, delay + 2))
                        
        if success_count > 0:
            st.toast(f"Recorded {success_count} responses. Run complete.")
            celebrate(
                "Dispatch complete",
                f"{success_count} responses were recorded successfully. Receipt saved, progress closed, and the run finished cleanly.",
                "success",
            )
            st.balloons()

elif step_bar == "02 PERSONA":
    pending_feedback = st.session_state.pop("pending_feedback", None)
    if pending_feedback:
        celebrate(pending_feedback["title"], pending_feedback["body"], pending_feedback["kind"])
    st.markdown('<div class="section-block" style="font-size: 1.3rem; font-family: \'Kodchasan\', sans-serif; font-weight: 600; border-bottom: 2px solid #FFC107; display: inline-block; padding-bottom: 5px; margin-bottom: 20px;">◎ Persona Lab</div>', unsafe_allow_html=True)
    if not current_proj.get("field_map"):
        st.warning("◎ Please scrape a form in 'Setup' before editing persona groups.")
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
            st.markdown(f'<div style="font-size: 1.1rem; font-family: \'Kodchasan\', sans-serif; font-weight: 600; margin-top: 20px; margin-bottom: 10px;">Editing: {p_name}</div>', unsafe_allow_html=True)
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

        if st.button("+ Save Persona Group Configuration"):
            if p_name and p_name != "+ Create New Persona Group":
                st.session_state.engine.save_persona(active_project, p_name, new_response_map)
                enabled_fields = sum(1 for v in new_response_map.values() if v.get("enabled"))
                template_total = sum(len(v.get("values", [])) for v in new_response_map.values())
                queue_feedback(
                    "Persona saved",
                    f"'{p_name}' is ready with {enabled_fields} enabled field(s) and {template_total} template value(s) for dispatch.",
                    "success",
                )
                st.toast(f"Saved persona '{p_name}' and prepared it for dispatch.")
                st.rerun()

st.markdown("---")
footer_left, footer_spacer, footer_right = st.columns([1, 7, 1])
with footer_left:
    st.markdown('<div class="footer-shell" style="color: #888888; font-size: 0.9rem;">Developed by Swarty</div>', unsafe_allow_html=True)
with footer_spacer:
    st.empty()
with footer_right:
    st.button(
        "Is the Admin Here?",
        key="footer_admin_button",
        type="secondary",
        use_container_width=False,
        on_click=open_admin_panel,
    )
