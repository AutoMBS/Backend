# Medical Categories Data API + RAG

## 📌 Overview

This is a **FastAPI** backend service that provides two main features:

- Query medical categories and statistics from an **SQLite** database
- Perform **Retrieval-Augmented Generation (RAG)** search using Qdrant for medical service item recommendations

---

## ⚙️ Setup

### 1. Clone the project / move into the project directory

```bash
cd your_project_folder
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate     # Mac/Linux
# .venv\Scripts\activate      # Windows PowerShell
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Qdrant (vector database)

Make sure Qdrant is running locally:

```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

---

## 🚀 Run the API

Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

Default endpoints:

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🗂️ Project Structure (example)

```
API/
├─ Route/
│  └─ rag.py              # RAG route definitions
├─ rag_service.py         # RAG core logic
├─ main.py                # FastAPI entrypoint
data/
├─ medical_categories.db  # SQLite database
├─ category_1_items_with_duration_split.csv
README.md
requirements.txt
```

---

## 📊 Vector Database Virtual

http://localhost:6333/dashboard#/collections/MBS

## 📖 Available Endpoints

### 1. Core API

- `/` → API info
- `/health` → Health check
- `/categories` → List all categories
- `/categories/{category_id}` → Get records for a category
- `/statistics` → Statistics summary
- `/filter` → Filter by age and time
- `/category1/filter` → Category 1 filters
- `/category3/filter` → Category 3 filters

### 2. RAG API

- `POST /MBS/code/suggest`
  Input free text (e.g., clinical note) to get candidate MBS items:

  ```json
  {
    "free_text": "Tightness in chest and shortness of breath...",
    "age": 90,
    "provider": "gp",
    "duration": 40
  }
  ```
