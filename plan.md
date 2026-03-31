# Simple HR Chatbot Project Plan

## 1. Project Goal

Build a simple and useful HR chatbot that answers common employee questions using company HR documents. The chatbot will use:

- RAG (Retrieval-Augmented Generation)
- Gemini API
- Python + FastAPI
- `uv` package manager
- ChromaDB as the vector database

The goal is to create a beginner-friendly project that is easy to build, understand, and extend later.

### Main use cases

- Answer questions about leave policy
- Answer questions about benefits
- Help with onboarding information
- Respond to common HR FAQ queries
- Show which document or section the answer came from

### Success criteria

- Easy local setup
- Clean and understandable code structure
- Useful answers based on HR documents
- Reduced hallucinations by using retrieved context
- Simple API that can later be connected to a web or chat UI

## 2. Architecture Overview

This project will use a straightforward RAG pipeline.

### High-level flow

1. HR documents are collected in a local folder.
2. Documents are cleaned and split into chunks.
3. Chunks are converted into embeddings.
4. Embeddings and chunk text are stored in ChromaDB.
5. FastAPI receives a user question.
6. Relevant chunks are retrieved from ChromaDB.
7. A prompt is built using the retrieved context.
8. Gemini API generates the final answer.
9. The API returns the answer with source references.

### Beginner-friendly design choices

- Use a local document folder instead of many external data sources
- Use ChromaDB to avoid PostgreSQL setup complexity
- Keep ingestion as a simple script
- Keep authentication and advanced scaling optional for later
- Focus first on correctness and simplicity

## 3. Main Components

## 3.1 Document Ingestion

Purpose: prepare HR files so they can be searched by the chatbot.

### Responsibilities

- Read HR files such as:
  - PDF files
  - DOCX files
  - TXT or Markdown files
- Extract text
- Clean unnecessary spaces and repeated noise
- Split text into smaller chunks
- Add basic metadata:
  - file name
  - section title if available
  - document type
- Generate embeddings for each chunk
- Store the chunks in ChromaDB

### Beginner scope

Start with a small number of documents, such as:

- Employee handbook
- Leave policy
- Benefits FAQ
- Onboarding guide

## 3.2 ChromaDB

Purpose: store document chunks and embeddings for semantic search.

### Why ChromaDB

- Very easy for beginners
- Fast to set up locally
- Good enough for a small or medium chatbot prototype
- No need to manage PostgreSQL or extensions

### What will be stored

- `id`
- `chunk_text`
- `embedding`
- `source`
- `section`
- `document_type`

## 3.3 Retriever

Purpose: fetch the most relevant chunks for a user question.

### Retrieval process

- Convert the user query into an embedding
- Search ChromaDB for the most similar chunks
- Return the top matching chunks
- Pass them into the prompt

### Simple retrieval strategy

- Start with top 3 to top 5 chunks
- Keep metadata simple
- Improve later only if answer quality is weak

## 3.4 Gemini API

Purpose: generate the answer using the retrieved HR context.

### Responsibilities

- Read the user question
- Read the retrieved HR document chunks
- Answer using only the provided context
- Avoid making up policies
- Say when the answer is not available in the documents
- Mention the source document in the response

## 3.5 FastAPI Backend

Purpose: provide a clean API for chatbot requests.

### Suggested endpoints

- `POST /chat`
  - Accepts a user question
  - Returns answer and sources
- `POST /ingest`
  - Loads documents and stores them in ChromaDB
- `GET /health`
  - Confirms the app is running

### Why FastAPI

- Easy to learn
- Great developer experience
- Automatic docs with Swagger UI
- Works well for Python-based AI applications

## 4. Folder Structure

Suggested simple structure:

```text
.
├── plan.md
├── pyproject.toml
├── uv.lock
├── README.md
├── .env.example
├── app
│   ├── main.py
│   ├── api
│   │   └── routes
│   │       ├── chat.py
│   │       ├── ingest.py
│   │       └── health.py
│   ├── core
│   │   ├── config.py
│   │   └── logging.py
│   ├── services
│   │   ├── chat_service.py
│   │   ├── retrieval_service.py
│   │   ├── prompt_service.py
│   │   └── gemini_service.py
│   ├── ingestion
│   │   ├── loaders.py
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   └── pipeline.py
│   └── db
│       └── chroma_client.py
├── data
│   ├── raw
│   └── processed
├── scripts
│   └── ingest_documents.py
└── tests
    ├── test_chat.py
    └── test_ingestion.py
```

### Structure notes

- `app/main.py` starts the FastAPI server
- `api/routes/` contains API endpoints
- `services/` contains the chatbot logic
- `ingestion/` handles document processing
- `db/chroma_client.py` handles ChromaDB operations
- `data/raw/` stores HR documents

## 5. Data Flow

## 5.1 Ingestion flow

1. Add HR documents to `data/raw/`
2. Run the ingestion script
3. Extract text from each file
4. Clean and split text into chunks
5. Generate embeddings
6. Store chunks and metadata in ChromaDB

## 5.2 Chat flow

1. User sends a question to `/chat`
2. FastAPI receives the request
3. The system retrieves relevant chunks from ChromaDB
4. A prompt is created using the user question and retrieved chunks
5. Gemini API generates the answer
6. The API returns the answer and source references

## 6. Prompt Strategy

The prompt should be simple, strict, and grounded in HR documents.

### Prompt goals

- Answer only from retrieved context
- Do not invent HR policies
- If the answer is missing, say so clearly
- Keep responses short and understandable
- Mention source documents when possible

### Suggested system instruction

The assistant should behave like an internal HR support chatbot that answers questions only from the provided company HR documents. If the context does not contain the answer, it should say that the information was not found and suggest contacting HR.

### Prompt format

1. System instruction
2. Retrieved HR context
3. User question

### Example response behavior

- If the answer exists in context, answer directly
- If the answer is partial, explain only what is supported by the context
- If no answer is found, respond with a safe fallback

## 7. Production Considerations

This project is intentionally simple, but a few production-minded practices should still be included.

## 7.1 Logging

- Log API requests and errors
- Log ingestion results
- Log when no documents are retrieved
- Avoid logging sensitive employee details

## 7.2 Security

- Store Gemini API key in environment variables
- Never hardcode secrets
- Validate API inputs
- Limit document sources to trusted HR files

## 7.3 Reliability

- Add basic error handling for:
  - missing files
  - failed embeddings
  - Gemini API failures
  - empty retrieval results
- Provide clear fallback responses

## 7.4 Scaling

For the first version:

- Run locally or on a small server
- Use ChromaDB locally or with persistent storage
- Keep the dataset small and focused

Later, if the chatbot grows:

- move to a more advanced vector database
- add authentication
- add caching
- deploy with Docker

## 8. Development Plan

## Phase 1: Setup

- Initialize project with `uv`
- Create FastAPI app
- Configure environment variables
- Add Gemini API connection

## Phase 2: Ingestion

- Add document loaders
- Build text chunking logic
- Generate embeddings
- Store chunks in ChromaDB

## Phase 3: Chat API

- Create `/chat` endpoint
- Retrieve matching chunks from ChromaDB
- Build prompt with context
- Return Gemini-generated answer with sources

## Phase 4: Improvement

- Improve chunking quality
- Add better source formatting
- Add simple tests
- Improve fallback responses

## 9. Future Enhancements

- Add a frontend chat UI
- Add conversation history
- Support more HR document types
- Add document upload from an admin page
- Add feedback buttons for answer quality
- Add role-based access for different HR content
- Replace or upgrade the vector database if needed later
- Add deployment with Docker and cloud hosting

## 10. Final Recommendation

As a beginner, the best approach is to keep the project small, local, and understandable. Use ChromaDB for vector storage, FastAPI for the backend, Gemini API for answers, and a small set of HR documents for the first version. Once the chatbot works well for common HR questions, you can gradually improve it with better retrieval, UI, authentication, and deployment features.
