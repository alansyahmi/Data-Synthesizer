# 📊 Data Synthesizer

A powerful "Research Simulation" platform was initially built for university-level academic research purposes. This tool automates the process of generating and submitting synthetic persona data to Google Forms for research validation and testing.

## 🚀 Key Features
- **Project-Based Workspaces**: Manage multiple research campaigns with unique URLs.
- **Smart Form Scraper**: Automatically detects field IDs and valid options (Radio, Dropdown, Checkbox).
- **Persona Lab**: Script granular responses for every question in your form.
- **Self-Healing Generator**: Fuzzy matches persona text against form options to prevent errors.
- **Human Simulation**: Random User-Agents and delays to mimic natural interaction.

## 🛠️ Installation

1. **Clone the repository** (or copy the folder).
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the App**:
   ```bash
   streamlit run app.py
   ```
4. **Alternative Run command**:
   ```bash
   py -m streamlit run app.py
   ```

## 🔒 Security & Secrets Management

The platform utilizes Streamlit's native secret management (`st.secrets`) to manage private configurations and API credentials securely.

1. **Local Secrets Configuration**:
   A local configuration file has been created at `.streamlit/secrets.toml`. This file is explicitly ignored in `.gitignore` to prevent secret leaks.
   
2. **Database Path Configuration**:
   Configure your database storage file path via secrets:
   ```toml
   PROJECTS_FILE = "projects.json"
   ```

3. **High-Fidelity AI Generation (Optional)**:
   To enable realistic, context-aware AI text generation for academic research validation, obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/) and paste it into `.streamlit/secrets.toml`:
   ```toml
   GEMINI_API_KEY = "your-api-key"
   ```
   If no key is configured, the engine automatically and securely falls back to the local deterministic deterministic mock generator.

## 📖 How to Use
1. **Setup**: Create a project and paste your Google Form `viewform` URL. Click "Analyze & Scrape."
2. **Persona Lab**: Create a new persona. Select which questions to include and provide specific options or text templates for each.
3. **Dispatcher**: Select your persona, set the number of submissions, and click "Execute Run."

## ⚠️ Ethical Use
This tool is intended for research purposes, synthetic data testing, and educational validation. Please use it ethically and in compliance with platform terms of service.
