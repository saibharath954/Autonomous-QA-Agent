# 🧠 Autonomous QA Agent  
### *Automated Test Case Generation + Selenium Script Generation*

This project implements an intelligent **Autonomous QA Agent** that ingests project documentation and HTML structure to automatically generate **test cases** and **Selenium Python scripts**.  
The agent builds a “testing brain” using RAG (Retrieval-Augmented Generation) and produces test outputs strictly grounded in the provided documents. 

---

# 📌 Features

### ✅ **Document Ingestion & Knowledge Base**
- Upload multiple support documents (PDF, MD, TXT, JSON).  
- Upload the html structure of the target webpage.  
- Automatic text extraction (PDF, MD, HTML, JSON parsers).  
- Chunking + vector embedding using Sentence Transformers.  
- Stores vectors in **ChromaDB** with metadata.

### ✅ **Test Case Generator**
- Generates **positive & negative functional test cases**.  
- Fully grounded in uploaded documents (no hallucinations).  
- Output formats:
  - JSON  
  - Markdown tables  
- Example (from assignment):  
  ```json
  {
    "Test_ID": "TC-005",
    "Feature": "Discount Code Validation",
    "Test_Scenario": "Enter invalid code",
    "Expected_Result": "Show error message",
    "Grounded_In": "checkout.html"
  }

### ✅ **Selenium Script Generator**

* Reads DOM structure from the html file.
* Extracts IDs, classes, names, or XPath.
* Produces clean, runnable Python Selenium scripts using:

  * WebDriverWait
  * Expected Conditions
  * Error handling
* Scripts strictly follow the HTML and documentation.

### ✅ **User Interface (Streamlit)**

* Upload zone for documents + HTML
* “Build Knowledge Base” button
* Prompt field for test case generation
* UI to pick a test case and generate Selenium script
* Syntax-highlighted code blocks

### ✨ **Tech Stack**

| Component       | Technology               |
| --------------- | ------------------------ |
| Frontend (UI)   | Streamlit                |
| Backend API     | FastAPI                  |
| Vector Database | ChromaDB                 |
| Embeddings      | Sentence Transformers    |
| LLM Provider    | OpenAI / Groq / Local HF |
| Parsing         | BeautifulSoup, pymupdf   |
| Hosting         | Render + Streamlit Cloud |

---

# 📂 Project Structure

```
📁 autonomous-qa-agent/
│
├── backend/
│ ├── app/
│ │ ├── main.py # FastAPI entrypoint
│ │ ├── services/
│ │ │ ├── embeddings.py # Embedding generator
│ │ │ ├── file_ingestion.py # PDF/HTML ingestion + chunking
│ │ │ ├── kb_builder.py # Knowledge base builder
│ │ │ ├── llm_provider.py # OpenAI/Groq/Local LLM wrapper
│ │ │ ├── rag_service.py # Retrieval + QA pipeline
│ │ │ ├── script_generator.py # Selenium script generator
│ │ │ └── vector_db.py # ChromaDB vector store
│ │ └── utils/
│ │ └── main.py # Helper utilities
│ │
│ ├── chroma_db/ # Persistent Chroma collections
│ ├── scripts/ # Backend helper scripts
│ ├── tests/ # Unit tests
│ └── uploaded_docs/ # User-uploaded files per session
│
├── project_assets/
│ ├── checkout.html # Source HTML for Selenium generator
│ ├── api_endpoints.json # API specification
│ ├── project_specs.md # System-level documentation
│ └── ui_ux_guide.txt # UX guidelines
│
├── streamlit_app/
│ ├── .streamlit/secrets.toml # Streamlit private keys
│ └── app.py # Streamlit UI
│
├── requirements.txt
├── render_requirements.txt
└── README.md

```

---

# 🛠️ Installation & Setup

### **1️⃣ Create Virtual Environment**

```bash
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### **2️⃣ Install Dependencies**

```bash
pip install -r requirements.txt
```

### Required Versions

* **Python 3.10+**
* **FastAPI 0.110+**
* **Streamlit 1.31+**
* **ChromaDB 0.4+**
* **Sentence Transformers**
* **Selenium 4.0+**

---

# ▶️ Running the Application

### **Start Backend (FastAPI)**

```bash
uvicorn backend.main:app --reload --port 8000
```

### **Start Frontend (Streamlit)**

```bash
streamlit run frontend/app.py
```

### Application Workflow

1. Upload support documents + `checkout.html`.
2. Click **Build Knowledge Base**.
3. Ask:

   ```
   Generate functional test cases for discount code validation
   ```
4. Select a test case → Click **Generate Selenium Script**.
5. Copy–paste the generated script into your automation framework.

---

# 📘 Usage Examples

### **Test Case Prompt**

```
Generate all positive and negative test cases for the discount code feature.
```

### **Selenium Script Prompt**

Triggered automatically when user selects a single test case.

### **- Example Output**

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

driver.get("checkout.html")

discount_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "discount-code"))
)
discount_input.send_keys("SAVE15")
```

---

# 📄 Explanation of Support Documents

| Document               | Purpose                                                          |
| ---------------------- | ---------------------------------------------------------------- |
| **product_specs.md**   | Contains business rules (e.g., discount % rules, shipping fees). |
| **ui_ux_guide.txt**    | Contains UI/UX rules (button color, error message style).        |
| **api_endpoints.json** | Optional API data for backend flows.                             |
| **checkout.html**      | DOM structure; required for Selenium selectors.                  |

These files are essential for grounding the QA agent’s reasoning.
Test cases must reference source documents exactly as required. 

---

# 🤝 Contributing

Pull requests are welcome.
For major changes, please open an issue first to discuss scope and design.

