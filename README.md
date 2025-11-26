# 🧠 Autonomous QA Agent  
### *Automated Test Case Generation + Selenium Script Generation*

The **Autonomous QA Agent** is an end-to-end intelligent testing system that ingests support documentation and the HTML structure of a target web application to automatically generate:

- **Functional Test Cases**
- **Positive & Negative Test Scenarios**
- **Grounded Explanations referencing source documents**
- **Runnable Selenium Python scripts**

The system builds a “Testing Brain” using **Retrieval-Augmented Generation (RAG)** and guarantees **zero hallucination** by grounding every result strictly in the uploaded documents.

---

## 📌 Features

### ✅ **Document Ingestion & Knowledge Base**
- Upload multiple support documents (PDF, MD, TXT, JSON).  
- Automatic extraction using:
  - PDF parsers (PyMuPDF)
  - HTML DOM parsing (BeautifulSoup)
  - Markdown/Text/JSON loaders
- Intelligent chunking using **RecursiveCharacterTextSplitter**
- Embedding generation using **Sentence Transformers**
- Stores metadata-rich vectors in **ChromaDB**  

### ✅ **Test Case Generator**
- Generates **positive & negative functional test cases**.  
- Fully grounded in uploaded documents (no hallucinations).  
- Output formats:
  - JSON  
  - Markdown tables  
- Example:  
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
* Generating RAG-based test cases
* UI to pick a test case and generate Selenium script
* Syntax-highlighted code blocks

---

## ✨ **Tech Stack**

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

## 📂 Project Structure

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

## 🏗️ Architecture

```
User → Streamlit UI → FastAPI Backend
           ↓              ↓
     Document Upload   Ingestion & Chunking
           ↓              ↓
      Build KB Button → Embeddings → ChromaDB
           ↓              ↓
      Test Case Prompt → RAG Retrieval → LLM
           ↓              ↓
  Selenium Script Request → DOM Parser → Script Generator → Output
``` 

---

## 🛠️ Installation & Setup

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/saibharath954/Autonomous-QA-Agent.git
cd autonomous-qa-agent
```

### **2️⃣ Set Up Backend Environment**
Navigate into the backend directory:
```bash
cd backend
```
Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### **3️⃣ Configure LLM Provider (Required)**
This system supports GROQ or Ollama (local LLM).
Create a `.env` file in the `backend/` folder:
```bash
touch .env
```
Add the following environment variables based on your choice:

Option A: Use GROQ (Recommended for Fast Inference)
```bash
GROQ_API_KEY=your_key_here
```
Option B: Use OLLAMA (Local Model)
```bash
OLLAMA_BASE_URL=http://localhost:11434
```

### **4️⃣ Install Backend Dependencies**

```bash
pip install -r requirements.txt
```

### **5️⃣ Start Backend (FastAPI)**
From inside `/backend` run:
```bash
uvicorn app.main:app --reload --port 8000
```
Backend will run at:
```bash
http://localhost:8000
```

### **6️⃣ Start Frontend (Streamlit)**
Open a second terminal and run:
```bash
cd streamlit_app
streamlit run app.py
```
Frontend will start at:
```bash
http://localhost:8501
```
---

## 📘 Usage Examples

1. Upload support documents + `checkout.html`.
2. Click **Build Knowledge Base**.
3. Go to Generate Test Cases tab and describe the feature to test.

Example Prompt:

```
Generate all positive and negative test cases for the discount code feature.
```
4. Go to Generate Selenium Script tab.
5. Select a test case → Click **Generate Selenium Script**.

Example Output:

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
6. Copy–paste the generated script into your automation framework.

---

## 📄 Explanation of Support Documents

| Document                       | Purpose                                                          |
| ------------------------------ | ---------------------------------------------------------------- |
| **product_specs.md**           | Contains business rules (e.g., discount % rules, shipping fees). |
| **ui_ux_guide.txt**            | Contains UI/UX rules (button color, error message style).        |
| **api_endpoints.json**         | Optional API data for backend flows.                             |
| **E Shop Checkout System.pdf** | Additional formal specifications or client documentation.        |
| **checkout.html**              | DOM structure; required for Selenium selectors.                  |

These files are essential for grounding the QA agent’s reasoning.
Test cases must reference source documents exactly as required. 

---

## 🧪 Quality Guarantees

* Zero hallucination — every test case references exact source documents.
* Traceable outputs — each test case includes a `Grounded_In` field.
* Script correctness — selectors come directly from DOM.
* Reproducible flow — deterministic grounding process.

---

## 🤝 Contributing

Pull requests are welcome.
For major changes, please open an issue first to discuss scope and design.

