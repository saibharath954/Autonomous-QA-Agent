import streamlit as st
import requests
import pandas as pd
import json

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Autonomous QA Agent", layout="wide")
st.title("🤖 Autonomous QA Agent")

# --- Sidebar: Dynamic Knowledge Base ---
with st.sidebar:
    st.header("📂 Knowledge Base Builder")
    st.info("Upload your project assets here. This builds the 'Brain' for the agent.")
    
    # Allow multiple files
    uploaded_files = st.file_uploader(
        "Upload Docs (PDF, MD, TXT, HTML, JSON)", 
        type=['pdf', 'md', 'txt', 'html', 'json'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("Build Knowledge Base"):
            with st.spinner("Processing documents & Building Vectors..."):
                files_payload = []
                for f in uploaded_files:
                    # Streamlit uploads need to be converted to tuple format for requests
                    files_payload.append(("files", (f.name, f.getvalue(), f.type)))
                
                try:
                    response = requests.post(f"{API_URL}/upload-documents", files=files_payload)
                    if response.status_code == 200:
                        st.success("✅ Knowledge Base Built Successfully!")
                        st.json(response.json())
                    else:
                        st.error(f"Build failed: {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

# --- Main Area: Test Case Generation ---
if 'test_cases' not in st.session_state:
    st.session_state['test_cases'] = []

st.subheader("1️⃣ Test Case Generation Agent")
user_query = st.text_area("Describe the feature to test (e.g., 'Generate test cases for valid discount codes')", height=80)

if st.button("Generate Test Cases"):
    if user_query:
        with st.spinner("Consulting Knowledge Base..."):
            try:
                payload = {"query": user_query}
                response = requests.post(f"{API_URL}/generate-testcases", data=payload)
                if response.status_code == 200:
                    data = response.json().get("results", [])
                    
                    # --- FIX: Ensure data is always a list ---
                    if isinstance(data, dict):
                        data = [data]
                    # -----------------------------------------

                    if isinstance(data, list) and len(data) > 0:
                        st.session_state['test_cases'] = data
                        st.success(f"Generated {len(data)} Test Cases")
                    else:
                        st.warning("No test cases generated. The agent might not have found enough info.")
                        st.session_state['test_cases'] = [] # Clear state on empty
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

if st.session_state['test_cases']:
    try:
        df = pd.DataFrame(st.session_state['test_cases'])
        st.dataframe(df, use_container_width=True)
    except ValueError as e:
        st.error(f"Data formatting error: {e}")
        st.json(st.session_state['test_cases']) # Show raw JSON so you can debug 

    st.markdown("---")
    st.subheader("2️⃣ Selenium Script Generation Agent")
    
    tc_options = [f"{tc.get('Test_ID', 'N/A')}: {tc.get('Test_Scenario', 'Unknown')}" for tc in st.session_state['test_cases']]
    selected_option = st.selectbox("Select a Test Case to Automate:", tc_options)
    
    if st.button("Generate Selenium Script"):
        selected_index = tc_options.index(selected_option)
        selected_test_case = st.session_state['test_cases'][selected_index]
        
        with st.spinner("Analyzing HTML & Writing Code..."):
            try:
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