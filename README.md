# HR Chatbot RAG

Beginner-friendly HR chatbot project using FastAPI, Gemini API, ChromaDB, and local PDF HR policies.

## Features

- Modern HTML, CSS, and JavaScript chat UI served by FastAPI
- Reads HR policy PDFs from `data/hr_policies_pdf`
- Splits policy text into chunks
- Stores embeddings in ChromaDB
- Retrieves relevant policy chunks for a user question
- Uses Gemini API to generate grounded answers
- Exposes health, ingestion, and chat endpoints

## Environment setup

Copy `.env.example` values into `.env` and set your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here`r`nGEMINI_EMBEDDING_MODEL=gemini-embedding-001
```

## Install dependencies

```bash
uv sync
```

## Run ingestion

```bash
uv run python scripts/ingest_documents.py
```

## Run the API

```bash
uv run uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/` for the UI.

## API endpoints

- `GET /api/v1/health`
- `POST /api/v1/ingest`
- `POST /api/v1/chat`
