# 📊 Data Synthesizer Pro

A powerful "Research Simulation" platform initially built for university-level academic research purposes. This tool automates the process of generating and submitting synthetic persona data to Google Forms for research validation and testing.

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

## 📖 How to Use
1. **Setup**: Create a project and paste your Google Form `viewform` URL. Click "Analyze & Scrape."
2. **Persona Lab**: Create a new persona. Select which questions to include and provide specific options or text templates for each.
3. **Dispatcher**: Select your persona, set the number of submissions, and click "Execute Run."

## ⚠️ Ethical Use
This tool is intended for research purposes, synthetic data testing, and educational validation. Please use it ethically and in compliance with platform terms of service.