import streamlit as st
import requests
import pandas as pd
import json
import uuid

# ====================================================
# SESSION INITIALIZATION
# ====================================================
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())

if 'test_cases' not in st.session_state:
    st.session_state['test_cases'] = []

if 'kb_built' not in st.session_state:
    st.session_state['kb_built'] = False

if 'uploaded_doc_names' not in st.session_state:
    st.session_state['uploaded_doc_names'] = []

if 'uploaded_html_name' not in st.session_state:
    st.session_state['uploaded_html_name'] = None

if st.query_params:
    st.query_params.clear()

API_URL = "http://localhost:8000"

# ====================================================
# PAGE CONFIGURATION
# ====================================================
st.set_page_config(
    page_title="Autonomous QA Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ====================================================
# CUSTOM CSS STYLING
# ====================================================
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Tabs Styling - CENTERED */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #1f2937; 
        padding: 10px;
        border-radius: 12px;
        border: 1px solid #374151;
        
        /* Centering Logic */
        display: flex;
        justify-content: center;
        flex-wrap: wrap; /* Allows wrapping on very small screens */
    }

    .stTabs [data-baseweb="tab"] {
        height: 55px;
        white-space: pre-wrap;
        background-color: #374151; 
        border-radius: 8px;
        color: #e5e7eb; 
        font-weight: 600;
        font-size: 16px;
        border: 1px solid transparent;
        transition: all 0.3s ease;
        flex-grow: 0; /* Prevents tabs from stretching awkwardly */
        min-width: 200px; /* Ensures consistent width for better visuals */
        display: flex; /* Helps center text inside the tab */
        align-items: center;
        justify-content: center;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #4b5563;
        color: #ffffff;
    }

    .stTabs [aria-selected="true"] {
        background-color: #6366f1 !important; 
        color: white !important;
        border: 1px solid #818cf8;
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.4);
    }
    
    /* Container styling */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .success-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .warning-box {
        background: #fefce8;
        padding: 1rem;
        border-radius: 10px;
        color: #92400e;
        margin: 1rem 0;
    }
    
    /* File upload area */
    .uploadedFile {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 1rem;
        background-color: #f8f9ff;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-ready {
        background-color: #38ef7d;
    }
    
    .status-pending {
        background-color: #feca57;
    }
</style>
""", unsafe_allow_html=True)

# ====================================================
# HEADER
# ====================================================
st.markdown('<h1 class="main-title">🤖 Autonomous QA Agent</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-Powered Test Case & Selenium Script Generation System</p>', unsafe_allow_html=True)

# ====================================================
# THREE-TAB LAYOUT
# ====================================================
tab1, tab2, tab3 = st.tabs([
    "📁 Upload & Build KB",
    "📋 Generate Test Cases",
    "🤖 Generate Selenium Script"
])

# ====================================================
# TAB 1: UPLOAD DOCUMENTS & BUILD KNOWLEDGE BASE
# ====================================================
with tab1:
    st.markdown("### 📁 Knowledge Base Construction")
    st.markdown("Upload your project documentation and HTML files to build the agent's knowledge base.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📄 Support Documents")
        st.markdown("Upload specifications, guidelines, API docs, etc.")
        uploaded_files = st.file_uploader(
            "Choose files",
            type=['pdf', 'md', 'txt', 'json'],
            accept_multiple_files=True,
            key="doc_uploader",
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            st.session_state['uploaded_doc_names'] = [f.name for f in uploaded_files]
            with st.expander(f"✅ {len(uploaded_files)} document(s) selected", expanded=True):
                for idx, f in enumerate(uploaded_files, 1):
                    st.markdown(f"**{idx}.** `{f.name}` ({f.size / 1024:.1f} KB)")
    
    with col2:
        st.markdown("#### 🌐 HTML File")
        st.markdown("Upload the HTML structure of a target web project.")
        uploaded_html = st.file_uploader(
            "Choose HTML file",
            type=['html'],
            key="html_uploader",
            label_visibility="collapsed"
        )
        
        if uploaded_html:
            st.session_state['uploaded_html_name'] = uploaded_html.name
            with st.expander("✅ HTML file selected", expanded=True):
                st.markdown(f"**File:** `{uploaded_html.name}` ({uploaded_html.size / 1024:.1f} KB)")
    
    st.markdown("---")
    
    # Status Display
    col_status1, col_status2, col_status3 = st.columns(3)
    
    with col_status1:
        doc_count = len(st.session_state.get('uploaded_doc_names', []))
        if doc_count > 0:
            st.markdown(f"<div class='info-box' style='text-align: center;'><h3>{doc_count}</h3>Support Docs</div>", unsafe_allow_html=True)
        else:
            st.info("📄 No documents uploaded")
    
    with col_status2:
        if st.session_state.get('uploaded_html_name'):
            st.markdown(f"<div class='info-box' style='text-align: center;'><h3>✓</h3>HTML Ready</div>", unsafe_allow_html=True)
        else:
            st.info("🌐 No HTML uploaded")
    
    with col_status3:
        if st.session_state.get('kb_built'):
            st.markdown(f"<div class='success-box' style='text-align: center;'><h3>✓</h3>KB Built</div>", unsafe_allow_html=True)
        else:
            st.info("🔨 KB Not Built")
    
    st.markdown("---")
    
    # Build Knowledge Base Button
    can_build = uploaded_files and len(uploaded_files) > 0
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        build_button = st.button(
            "🔨 Build Knowledge Base",
            disabled=not can_build,
            type="primary",
            use_container_width=True
        )
    
    if not can_build:
        st.warning("⚠️ Please upload at least one support document to build the knowledge base.")
    
    if build_button and can_build:
        with st.status("🔄 Building Knowledge Base...", expanded=True) as status:
            st.write("📤 Uploading documents...")
            files_payload = []
            for f in uploaded_files:
                files_payload.append(("files", (f.name, f.getvalue(), f.type)))
            
            try:
                st.write("🔗 Connecting to backend...")
                headers = {"X-Session-ID": st.session_state['session_id']}
                response = requests.post(f"{API_URL}/upload-documents", files=files_payload, headers=headers)
                
                if response.status_code == 200:
                    st.write("✅ Processing complete!")
                    st.session_state['kb_built'] = True
                    status.update(label="✅ Knowledge Base Built Successfully!", state="complete", expanded=False)
                    st.balloons()
                    st.toast("✅ Knowledge Base is ready!", icon="✅")
                    st.rerun()
                else:
                    st.error(f"❌ Build failed: {response.text}")
                    status.update(label="❌ Build Failed", state="error")
            except Exception as e:
                st.error(f"❌ Connection Error: {e}")
                status.update(label="❌ Connection Error", state="error")

# ====================================================
# TAB 2: GENERATE TEST CASES
# ====================================================
with tab2:
    st.markdown("### 📋 Test Case Generation Agent")
    
    if not st.session_state.get('kb_built'):
        st.markdown('<div class="warning-box">⚠️ <strong>Knowledge Base Not Built</strong><br>Please go to Tab 1 and build the knowledge base first.</div>', unsafe_allow_html=True)
    else:
        st.markdown("Ask the agent to generate test cases based on the uploaded documentation.")
        
        # Query Input
        with st.container():
            user_query = st.text_area(
                "🎯 Describe the feature to test",
                placeholder="Example: Generate positive and negative test cases for the discount code feature",
                height=100,
                help="Be specific about what you want to test"
            )
            
            col_gen1, col_gen2, col_gen3 = st.columns([1, 2, 1])
            with col_gen2:
                generate_button = st.button(
                    "✨ Generate Test Cases",
                    disabled=not user_query.strip(),
                    type="primary",
                    use_container_width=True
                )
        
        if generate_button and user_query.strip():
            with st.status("🤖 Consulting Knowledge Base...", expanded=True) as status:
                st.write("🔍 Analyzing your query...")
                st.write("📚 Retrieving relevant documentation...")
                
                try:
                    headers = {"X-Session-ID": st.session_state['session_id']}
                    payload = {"query": user_query}
                    response = requests.post(f"{API_URL}/generate-testcases", data=payload, headers=headers)
                    
                    if response.status_code == 200:
                        st.write("✅ Processing response...")
                        data = response.json().get("results", [])
                        
                        # --- FIX: Ensure data is always a list ---
                        if isinstance(data, dict):
                            data = [data]
                        # -----------------------------------------

                        if isinstance(data, list) and len(data) > 0:
                            st.session_state['test_cases'] = data
                            status.update(label=f"✅ Generated {len(data)} Test Cases!", state="complete", expanded=False)
                            st.toast(f"✅ {len(data)} test cases generated successfully!", icon="✨")
                            st.rerun()
                        else:
                            st.warning(
                                "⚠️ **No test cases were generated.**\n\n"
                                "**Possible reasons:**\n"
                                "- The system could not find relevant information in the knowledge base.\n"
                                "- Your query may be too short or unclear.\n"
                                "- The agent could not extract structured test cases from the response.\n\n"
                                "💡 **Try:**\n"
                                "- Rephrasing your request with more details\n"
                                "- Uploading more detailed documents\n"
                                "- Being more specific about the feature to test"
                            )
                            st.session_state['test_cases'] = []
                            status.update(label="⚠️ No test cases generated", state="error")
                    else:
                        st.error(f"❌ Error: {response.status_code}")
                        status.update(label="❌ Generation Failed", state="error")
                except Exception as e:
                    st.error(f"❌ Connection Error: {e}")
                    status.update(label="❌ Connection Error", state="error")
        
        # Display Test Cases
        if st.session_state.get('test_cases'):
            st.markdown("---")
            st.markdown("### 📊 Generated Test Cases")
            
            try:
                df = pd.DataFrame(st.session_state['test_cases'])
                
                with st.container():
                    st.markdown(f"**Total Test Cases:** `{len(df)}`")
                    st.dataframe(
                        df,
                        use_container_width=True,
                        height=400
                    )
                    
                    col_exp1, col_exp2 = st.columns(2)
                    with col_exp1:
                        if st.button("📥 Download as CSV", use_container_width=True):
                            csv = df.to_csv(index=False)
                            st.download_button(
                                "⬇️ Click to Download",
                                csv,
                                "test_cases.csv",
                                "text/csv",
                                use_container_width=True
                            )
                    with col_exp2:
                        if st.button("📋 Download as JSON", use_container_width=True):
                            json_str = json.dumps(st.session_state['test_cases'], indent=2)
                            st.download_button(
                                "⬇️ Click to Download",
                                json_str,
                                "test_cases.json",
                                "application/json",
                                use_container_width=True
                            )
                
            except ValueError as e:
                st.error(f"❌ Data formatting error: {e}")
                with st.expander("🔍 View Raw JSON Data"):
                    st.json(st.session_state['test_cases'])

# ====================================================
# TAB 3: GENERATE SELENIUM SCRIPT
# ====================================================
with tab3:
    st.markdown("### 🤖 Selenium Script Generation Agent")
    
    if not st.session_state.get('test_cases'):
        st.markdown('<div class="warning-box">⚠️ <strong>No Test Cases Available</strong><br>Please go to Tab 2 and generate test cases first.</div>', unsafe_allow_html=True)
    else:
        st.markdown("Select a test case to convert into an automated Selenium script.")
        
        # Test Case Selection
        tc_options = [f"{tc.get('Test_ID', 'N/A')}: {tc.get('Test_Scenario', 'Unknown')}" for tc in st.session_state['test_cases']]
        
        with st.container():
            selected_option = st.selectbox(
                "🎯 Select Test Case",
                tc_options,
                help="Choose which test case to automate"
            )
            
            # Show selected test case details
            if selected_option:
                selected_index = tc_options.index(selected_option)
                selected_test_case = st.session_state['test_cases'][selected_index]
                
                with st.expander("📄 View Selected Test Case Details", expanded=True):
                    st.json(selected_test_case)
        
        st.markdown("---")
        
        # Generate Script Button
        col_script1, col_script2, col_script3 = st.columns([1, 2, 1])
        with col_script2:
            generate_script_button = st.button(
                "⚡ Generate Selenium Script",
                type="primary",
                use_container_width=True
            )
        
        if generate_script_button:
            selected_index = tc_options.index(selected_option)
            selected_test_case = st.session_state['test_cases'][selected_index]
            
            with st.status("🔄 Generating Selenium Script...", expanded=True) as status:
                st.write("🔍 Analyzing HTML structure...")
                st.write("📝 Writing Python code...")
                st.write("🎯 Mapping selectors...")
                
                try:
                    payload = {"testcase_json": json.dumps(selected_test_case)}
                    response = requests.post(f"{API_URL}/generate-selenium-script", data=payload)
                    
                    if response.status_code == 200:
                        script_content = response.json().get("script", "")
                        st.write("✅ Script generated successfully!")
                        status.update(label="✅ Script Generated!", state="complete", expanded=True)
                        
                        st.markdown("---")
                        st.markdown("### 🐍 Generated Python Selenium Script")
                        
                        with st.container():
                            st.code(script_content, language='python', line_numbers=True)
                            
                            col_download1, col_download2, col_download3 = st.columns([1, 2, 1])
                            with col_download2:
                                st.download_button(
                                    "📥 Download Script",
                                    script_content,
                                    f"test_script_{selected_test_case.get('Test_ID', 'unknown')}.py",
                                    "text/x-python",
                                    use_container_width=True
                                )
                        
                        st.toast("✅ Selenium script generated successfully!", icon="🎉")
                        st.success("✨ **Script ready!** You can copy or download the code above.")
                        
                    else:
                        st.error(f"❌ Failed to generate script: {response.status_code}")
                        status.update(label="❌ Generation Failed", state="error")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    status.update(label="❌ Error Occurred", state="error")

# ====================================================
# FOOTER
# ====================================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    "🤖 <strong>Autonomous QA Agent</strong> | Powered by AI<br>"
    "Built with Streamlit • FastAPI • LLMs • RAG"
    "</div>",
    unsafe_allow_html=True
)