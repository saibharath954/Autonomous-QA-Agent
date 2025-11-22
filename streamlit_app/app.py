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

# --- Main Area: Test Case Generation ---
st.subheader("1️⃣ Test Case Generation Agent")
user_query = st.text_area("Describe the feature to test (e.g., 'Generate test cases for the Discount Code feature')", height=100)

if st.button("Generate Test Cases"):
    if user_query:
        with st.spinner("Consulting Knowledge Base & Generating Cases..."):
            try:
                payload = {"query": user_query}
                response = requests.post(f"{API_URL}/generate-testcases", data=payload)
                
                if response.status_code == 200:
                    data = response.json().get("results", [])
                    
                    if isinstance(data, list) and len(data) > 0:
                        st.success(f"Generated {len(data)} Test Cases")
                        
                        # Display as Table
                        df = pd.DataFrame(data)
                        st.dataframe(df, use_container_width=True)
                        
                        # Store in session state for Phase 3 (Script Generation)
                        st.session_state['test_cases'] = data
                    else:
                        st.warning("No test cases generated. Check the agent response or document context.")
                        st.json(data) # Show raw if error
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Connection Error: {e}")
    else:
        st.info("Please enter a query first.")