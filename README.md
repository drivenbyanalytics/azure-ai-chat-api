## 🛠️ Tech Stack
 - **FastAPI** (API server)
 - **LangChain** (RecursiveCharacterTextSplitter, AzureOpenAIEmbeddings)
 - **Azure Cosmos DB** (file metadata)
 - **Azure AI Search** (vector index for chunks)

## Local Development Guide

### 1. Prerequisites
Make sure you have the following installed:
 - Python 3.11+ (or compatible version)
 - pip for installing packages
 - virtualenv (optional but recommended)
 - Git

### 2. Setup the Environment
#### 1. Clone the repository (if needed):
```bash
    git clone git@github.com:drivenbyanalytics/azure-ai-chat-api.git
    cd azure-ai-chat-api
```
#### 2. Create a virtual environment (recommended):
```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate     # Windows
```
#### 3. Install dependencies:
```bash
    pip install -r requirements.txt
```
#### 3. Environment variables:
    - Copy the ***example.env*** and rename it to ***.env***
    - Fill in the correct values for each key in the ***.env*** file
#### 4. Auzenticate in Azure:
```bash
    az login
``` 
### 3. Running FastAPI Locally
```bash
    fastapi dev api/main.py --port 8000
```
-  main → Python file name (without .py) where app = FastAPI() is defined
- --port 8000 → port number (can be changed)

Swagger UI (interactive API docs) at: http://localhost:8000/docs

Redoc documentation at: http://localhost:8000/redoc
