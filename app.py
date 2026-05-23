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

if 'uploader_id' not in st.session_state:
    st.session_state.uploader_id = 0

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
tab_setup, tab_run, tab_lab, tab_admin = st.tabs(["⚙️ Setup", "⚡ Dispatcher", "🧪 Persona Lab", "🔑 Admin Panel"])

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
        # Enforce UMS student email validation (Accountability Gate)
        st.subheader("🎓 1. Accountability Gate")
        student_email = st.text_input(
            "Enter your official UMS Email Address (@student.ums.edu.my or @ums.edu.my)", 
            placeholder="e.g. name@student.ums.edu.my",
            key=f"email_input_{st.session_state.uploader_id}"
        )
        email_valid = False
        if student_email:
            if "ums.edu.my" in student_email.lower().strip():
                st.success("✅ Email verified: Official UMS domain.")
                email_valid = True
            else:
                st.error("❌ Email invalid: Must be a UMS domain (containing 'ums.edu.my').")
        else:
            st.info("💡 Please enter your student email to proceed.")

        st.markdown("---")

        # Tier Selector Toggles
        st.subheader("⚖️ 2. Tier Selection")
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
            st.subheader("📝 3. Context & Human Baselines")
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
            
            with st.expander("📥 Get Sample Baseline Templates"):
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
                    st.success(f"✅ Baseline parsed successfully! Found {len(baseline_responses)} human responses.")
                    with st.expander("🔍 Preview Baseline Data"):
                        st.write(baseline_responses)
                else:
                    st.error(f"❌ Error: {parsed_res}")
                    baseline_valid = False
            else:
                st.warning("⚠️ Human baseline responses are required for Premium Tier context-aware generation (Minimum 10).")
                baseline_valid = False
                
            st.markdown("---")

        # Dispatch Configuration
        st.subheader("⚙️ 4. Run Configuration")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            flavor = st.selectbox("Select Persona Group", list(current_proj["personas"].keys()))
            limit = st.slider("Submissions (Max 50 per transaction)", 1, 50, 3)
        with col_s2:
            delay = st.slider("Min Delay (sec)", 1, 10, 3)

        st.markdown("---")

        # Payment Interface Box
        st.subheader("💳 5. Payment Verification")
        st.write("Scan the DuitNow QR code below to complete the transaction.")
        
        pay_col1, pay_col2 = st.columns([1, 1.5])
        with pay_col1:
            import os
            if os.path.exists("duitnow_qr_code.png"):
                st.image("duitnow_qr_code.png", caption="UMS Student DuitNow QR Code", width=260)
            else:
                st.error("DuitNow QR Code asset missing from workspace!")
        
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
                        st.warning("⚠️ Could not render receipt image preview. The uploaded file contains invalid image data.")
                else:
                    st.success(f"📄 Receipt file '{receipt_file.name}' ready.")

        st.markdown("---")

        # Submission Check
        ready_to_submit = False
        if email_valid and receipt_file:
            if not is_premium or (is_premium and baseline_valid):
                ready_to_submit = True
                
        # Main execution button locked until conditions are met
        if not ready_to_submit:
            st.info("🔒 The dispatch button is locked. Please enter a valid UMS email, configure necessary baseline data (Premium only), and upload your transaction receipt.")
            
        # Action Buttons Layout
        btn_col1, btn_col2 = st.columns([4, 1])
        with btn_col1:
            execute_button = st.button(
                "🚀 Execute Run", 
                disabled=not ready_to_submit,
                help="Unlocks after email validation, human baseline upload (for Premium), and receipt verification."
            )
        with btn_col2:
            if st.button("🧹 Clear Form State"):
                st.session_state.uploader_id += 1
                st.rerun()

        if execute_button:
            # First, save receipt
            receipt_bytes = receipt_file.getvalue()
            saved_path = st.session_state.engine.save_receipt(student_email, receipt_file.name, receipt_bytes)
            st.info(f"💾 Receipt saved successfully to: `{saved_path}`")
            
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

with tab_admin:
    st.header("🔑 Admin Panel")
    
    # Retrieve Admin Password from secrets
    correct_pass = None
    try:
        correct_pass = st.secrets.get("ADMIN_PASSWORD")
    except Exception:
        pass
        
    if not correct_pass:
        st.warning("⚠️ Admin Password is not configured. Please add `ADMIN_PASSWORD = \"yourpassword\"` to `.streamlit/secrets.toml` to access this panel.")
    else:
        admin_pass_input = st.text_input("Enter Admin Password", type="password", key="admin_password_input_field")
        if admin_pass_input == correct_pass:
            st.success("🔓 Access Granted.")
            st.subheader("📊 Transaction Logs & Receipts")
            
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
                
                # Render table using markdown table
                st.markdown("| No | Timestamp | Student Email | File Name |")
                st.markdown("| --- | --- | --- | --- |")
                for log in logs:
                    st.markdown(f"| {log['No']} | {log['Timestamp']} | {log['Student Email']} | {log['File Name']} |")
                
                st.markdown("---")
                st.subheader("🔍 Receipt File Viewer")
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
                            st.warning("⚠️ Could not render receipt image preview. File may be corrupted or contains invalid image data.")
                    else:
                        st.info("📄 PDF or Binary file receipt. Click below to download and inspect.")
                        
                    st.download_button(
                        label=f"Download {selected_log['File Name']}",
                        data=file_bytes,
                        file_name=selected_log["File Name"],
                        mime="application/octet-stream"
                    )

st.markdown("---")
st.caption("Developed for Technopreneurship | UMS")
