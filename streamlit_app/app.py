import streamlit as st
import requests
import pandas as pd
import json

# Backend URL
API_URL = "http://localhost:8000"

st.set_page_config(page_title="Autonomous QA Agent", layout="wide")

st.title("🤖 Autonomous QA Agent")
st.markdown("### AI-Powered Test Case & Script Generator")

# --- Sidebar: Knowledge Base ---
with st.sidebar:
    st.header("📂 Knowledge Base")
    uploaded_file = st.file_uploader("Upload Project Docs", type=['pdf', 'md', 'txt', 'html', 'json'])
    
    if uploaded_file is not None:
        if st.button("Process & Build KB"):
            with st.spinner("Ingesting document..."):
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                # 1. Upload
                response = requests.post(f"{API_URL}/upload", files=files)
                if response.status_code == 200:
                    st.success(f"Uploaded {uploaded_file.name}")
                    # Note: For this simplified flow, we assume the backend builds the KB 
                    # immediately or via a separate trigger. In `main.py` upload just parses.
                    # We might need a direct 'build' trigger here if not automatic.
                    # For now, let's assume we are using the local file path method for the assignment.
                else:
                    st.error("Upload failed")

# --- Session State Init ---
if 'test_cases' not in st.session_state:
    st.session_state['test_cases'] = []

# --- Main Area: Test Case Generation ---
st.subheader("1️⃣ Test Case Generation Agent")
user_query = st.text_area("Describe the feature to test (e.g., 'Generate test cases for the Discount Code feature')", height=80)

if st.button("Generate Test Cases"):
    if user_query:
        with st.spinner("Consulting Knowledge Base..."):
            try:
                payload = {"query": user_query}
                response = requests.post(f"{API_URL}/generate-testcases", data=payload)
                if response.status_code == 200:
                    data = response.json().get("results", [])
                    st.session_state['test_cases'] = data # Save to session
                    st.success(f"Generated {len(data)} Test Cases")
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# Display Results & Selection for Phase 3
if st.session_state['test_cases']:
    # Convert list of dicts to DataFrame for display
    df = pd.DataFrame(st.session_state['test_cases'])
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("2️⃣ Selenium Script Generation Agent")
    
    # Create a selection list mapping Test IDs to the actual objects
    tc_options = [f"{tc['Test_ID']}: {tc['Test_Scenario']}" for tc in st.session_state['test_cases']]
    selected_option = st.selectbox("Select a Test Case to Automate:", tc_options)
    
    if st.button("Generate Selenium Script"):
        # Find the specific dict object for the selected ID
        selected_index = tc_options.index(selected_option)
        selected_test_case = st.session_state['test_cases'][selected_index]
        
        with st.spinner("Analyzing HTML & Writing Code..."):
            try:
                # Send as JSON string form data
                payload = {"testcase_json": json.dumps(selected_test_case)}
                response = requests.post(f"{API_URL}/generate-selenium-script", data=payload)
                
                if response.status_code == 200:
                    script_content = response.json().get("script", "")
                    st.subheader("🐍 Generated Python Selenium Script")
                    st.code(script_content, language='python')
                else:
                    st.error("Failed to generate script")
            except Exception as e:
                st.error(f"Error: {e}")