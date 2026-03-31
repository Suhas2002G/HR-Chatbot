# HR Chatbot Project Plan

## 1. Project Goal

Build a production-grade HR chatbot that answers employee questions using internal HR knowledge sources and company policy documents. The system will use Retrieval-Augmented Generation (RAG) to ground responses in approved content, Gemini API for response generation, Python + FastAPI for backend services, and `uv` for dependency and environment management.

### Primary objectives

- Provide accurate, policy-aligned answers to HR-related questions.
- Reduce repetitive HR support workload by automating common queries.
- Support secure retrieval from internal knowledge sources such as handbooks, leave policies, benefits documents, onboarding guides, and FAQ content.
- Return responses with citations or source references to improve trust and auditability.
- Enable maintainable, scalable deployment suitable for internal enterprise use.

### Success criteria

- High answer relevance for common HR queries.
- Low hallucination rate through retrieval grounding and prompt controls.
- Fast API response times under expected concurrency.
- Clear observability for requests, retrieval quality, and system failures.
- Secure handling of employee questions, documents, and API credentials.

## 2. Architecture Overview

The system will follow a modular RAG architecture composed of offline ingestion pipelines and an online query-serving path.

### High-level architecture

1. HR documents are collected from approved data sources.
2. Documents are cleaned, normalized, chunked, and enriched with metadata.
3. Chunks are embedded and stored in a vector database.
4. A FastAPI backend receives user questions.
5. The retriever finds relevant chunks from the vector store.
6. The prompt builder combines user query, retrieved context, instructions, and guardrails.
7. Gemini API generates a grounded answer.
8. The API returns the answer, citations, confidence signals, and optional fallback messaging.

### Recommended deployment model

- Backend API service: FastAPI application deployed as a containerized service.
- Background ingestion jobs: separate worker process or scheduled pipeline.
- Vector database: managed or self-hosted, depending infrastructure requirements.
- Object/document storage: source of truth for raw and processed documents.
- Monitoring stack: logs, metrics, tracing, and alerting integrated with deployment platform.

## 3. Core Components

## 3.1 Ingestion Pipeline

Purpose: convert raw HR documents into clean, searchable knowledge units.

### Responsibilities

- Load documents from supported sources:
  - PDF handbooks
  - DOCX policy documents
  - HTML/wiki pages
  - CSV/structured HR FAQs
- Normalize text and extract metadata.
- Remove boilerplate and irrelevant sections.
- Split documents into semantically useful chunks.
- Attach metadata such as document name, source URL/path, policy category, effective date, region, department, and access level.
- Generate embeddings for chunks.
- Upsert chunk records into the vector database.

### Production requirements

- Idempotent ingestion runs.
- Versioning for source documents and chunk records.
- Incremental reindexing for changed content.
- Validation for corrupt or empty documents.
- Audit logs for ingestion status and failures.

## 3.2 Vector Database

Purpose: store embeddings and metadata for efficient semantic retrieval.

### Candidate options

- PostgreSQL with `pgvector` for strong operational simplicity and relational metadata filtering.
- Qdrant for dedicated vector search performance and filtering support.
- Weaviate or Pinecone if managed cloud operations are preferred.

### Recommendation

Use PostgreSQL + `pgvector` if the team wants simpler infrastructure and SQL-friendly metadata queries. Use Qdrant if vector retrieval performance and scaling flexibility are the primary concern.

### Stored fields

- `chunk_id`
- `document_id`
- `text`
- `embedding`
- `source_name`
- `source_type`
- `section_title`
- `policy_category`
- `effective_date`
- `region`
- `department`
- `access_level`
- `checksum`
- `created_at`
- `updated_at`

## 3.3 Retriever

Purpose: identify the most relevant context for each user question.

### Retrieval strategy

- Hybrid retrieval preferred:
  - Semantic similarity search using embeddings
  - Optional keyword/BM25 retrieval for exact policy terms
- Metadata filtering:
  - Geography-specific policies
  - Full-time vs contractor policies
  - Department-specific guidance
  - Access-control restrictions
- Top-k retrieval followed by reranking if needed

### Enhancements

- Query rewriting for ambiguous employee questions
- Multi-query retrieval for broad or multi-part questions
- Reranker model for improved precision
- Query classification to route policy questions vs escalation workflows

## 3.4 LLM Layer

Purpose: generate grounded, safe, and HR-appropriate answers using Gemini API.

### Responsibilities

- Accept structured prompt with instructions and retrieved context.
- Generate concise, policy-grounded answers.
- Refuse to invent policies not present in the provided context.
- Ask clarifying questions when the query is ambiguous.
- Provide source citations and escalation guidance when appropriate.

### Gemini usage considerations

- Use a fast model tier for low-latency chat responses.
- Optionally use a higher-capability model for complex policy synthesis or internal evaluation workflows.
- Keep model configuration explicit:
  - temperature
  - token limits
  - safety settings
  - timeout and retry strategy

## 3.5 API Layer

Purpose: expose secure, testable endpoints for chatbot interactions and operations.

### Suggested endpoints

- `POST /api/v1/chat`
  - Accepts user question, user context, and optional conversation history
  - Returns answer, citations, and response metadata
- `POST /api/v1/ingest`
  - Triggers document ingestion or reindexing
- `GET /api/v1/health`
  - Liveness and readiness checks
- `GET /api/v1/metrics`
  - Prometheus-compatible operational metrics
- `GET /api/v1/documents`
  - Optional admin endpoint for indexed document inspection

### API expectations

- Strong request/response schemas with Pydantic
- Authentication and authorization for internal use
- Rate limiting and request size validation
- Trace IDs for debugging and observability

## 4. Folder Structure

Suggested production-oriented layout:

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
│   │   ├── routes
│   │   │   ├── chat.py
│   │   │   ├── ingest.py
│   │   │   └── health.py
│   │   └── dependencies.py
│   ├── core
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── security.py
│   │   └── exceptions.py
│   ├── models
│   │   ├── chat.py
│   │   ├── document.py
│   │   └── common.py
│   ├── services
│   │   ├── chat_service.py
│   │   ├── retrieval_service.py
│   │   ├── prompt_service.py
│   │   ├── llm_service.py
│   │   └── citation_service.py
│   ├── ingestion
│   │   ├── loaders
│   │   │   ├── pdf_loader.py
│   │   │   ├── docx_loader.py
│   │   │   ├── html_loader.py
│   │   │   └── faq_loader.py
│   │   ├── chunking.py
│   │   ├── cleaning.py
│   │   ├── embeddings.py
│   │   ├── pipeline.py
│   │   └── metadata.py
│   ├── db
│   │   ├── vector_store.py
│   │   ├── postgres.py
│   │   └── repositories
│   │       ├── documents.py
│   │       └── chunks.py
│   └── utils
│       ├── ids.py
│       ├── time.py
│       └── text.py
├── scripts
│   ├── ingest_documents.py
│   ├── reindex.py
│   └── evaluate_retrieval.py
├── tests
│   ├── unit
│   ├── integration
│   └── e2e
├── data
│   ├── raw
│   ├── processed
│   └── fixtures
├── docs
│   ├── architecture.md
│   ├── api.md
│   └── runbooks
└── deployments
    ├── Dockerfile
    ├── docker-compose.yml
    └── k8s
```

### Structure rationale

- `app/` contains runtime application code.
- `ingestion/` isolates offline document processing logic.
- `services/` contains business orchestration for chat and retrieval.
- `db/` abstracts vector store and persistence details.
- `scripts/` contains operational entry points.
- `tests/` separates unit, integration, and end-to-end coverage.
- `deployments/` centralizes deployment assets.

## 5. Data Flow

## 5.1 Offline indexing flow

1. Collect documents from approved HR knowledge sources.
2. Validate file type, checksum, and source metadata.
3. Extract raw text and document structure.
4. Clean text and remove repeated headers, footers, and noise.
5. Chunk content using policy-aware chunking rules.
6. Generate embeddings for each chunk.
7. Store chunk text, embedding, and metadata in the vector database.
8. Record ingestion logs, version info, and indexing status.

## 5.2 Online question-answering flow

1. User sends a question to `POST /api/v1/chat`.
2. API authenticates request and attaches user context.
3. Query is normalized and optionally classified.
4. Retriever fetches top relevant chunks with metadata filters.
5. Prompt builder assembles system instructions, context, and conversation history.
6. Gemini API generates an answer grounded in retrieved documents.
7. Post-processing formats citations, confidence indicators, and fallback guidance.
8. API returns structured response and logs the interaction for observability.

## 6. Prompt Strategy

Prompting is critical for keeping the chatbot accurate, bounded, and useful in an HR setting.

### System prompt goals

- Define the assistant as an internal HR policy assistant.
- Require answers to be grounded only in retrieved context.
- Instruct the model not to fabricate benefits, eligibility rules, or legal guidance.
- Require explicit acknowledgment when information is missing or ambiguous.
- Encourage concise, employee-friendly language.
- Instruct the model to cite the relevant source chunks or document names.
- Route sensitive cases to HR escalation when needed.

### Suggested prompt layers

1. System instruction
   - Defines role, boundaries, tone, and refusal behavior.
2. Policy guardrails
   - No invented answers
   - No legal, medical, or financial advice beyond documented policy
   - Escalate when policy is unavailable or conflicting
3. Retrieved context block
   - Ranked chunks with source metadata
4. User question
   - Current query
5. Conversation summary
   - Optional short memory for continuity without excessive token usage

### Example answer rules

- If context clearly answers the question, respond directly and cite sources.
- If context partially answers, provide the known part and state what is unclear.
- If no relevant context is found, say that the information could not be verified and recommend contacting HR.
- If multiple policies conflict, mention the conflict and advise escalation.

### Prompt optimization plan

- Evaluate prompts against a curated HR test set.
- Measure hallucination rate, citation accuracy, and completeness.
- Tune chunk size, top-k, and instruction wording together.
- Add query-type specific prompt templates for leave, payroll, benefits, and onboarding topics.

## 7. Production Considerations

## 7.1 Logging and Observability

### Logging

- Use structured JSON logging.
- Include request ID, user/session ID, latency, retrieval count, model name, and error context.
- Mask or avoid sensitive personal data in logs.

### Metrics

- API latency
- Retrieval latency
- Gemini API latency and error rate
- Vector search latency
- Cache hit rate
- Rate of no-context responses
- Token usage and cost per request

### Tracing

- Trace end-to-end path across API, retrieval, prompt generation, and LLM call.
- Use OpenTelemetry-compatible tracing where possible.

## 7.2 Scaling

### Backend scaling

- Run FastAPI behind a production ASGI server such as Uvicorn with Gunicorn where appropriate.
- Scale stateless API replicas horizontally.
- Separate ingestion workers from chat-serving instances.

### Retrieval scaling

- Use connection pooling for database access.
- Add caching for repeated queries and document metadata.
- Evaluate dedicated vector DB deployment for larger corpora and higher concurrency.

### Performance targets

- Keep p95 chat latency within acceptable internal SLA.
- Optimize chunking and retrieval before increasing model complexity.
- Use async I/O for external API and database operations.

## 7.3 Security

### Authentication and authorization

- Enforce internal auth, such as SSO or JWT-based authentication.
- Apply role-based access control for admin and ingestion endpoints.
- Filter retrieval results based on document access level and employee scope.

### Secret management

- Store Gemini API keys and database credentials in a secret manager.
- Never commit secrets to source control.
- Rotate credentials regularly.

### Data protection

- Encrypt data in transit with TLS.
- Encrypt sensitive stored data at rest.
- Minimize storage of chat transcripts unless required by business policy.
- Apply retention policies for logs and conversation data.

### Application hardening

- Validate all inputs with schema enforcement.
- Rate-limit public-facing or internal high-risk endpoints.
- Sanitize uploaded documents and reject unsupported formats.
- Protect admin endpoints behind stronger controls.

## 7.4 Reliability

- Configure retries with backoff for transient Gemini API and database failures.
- Use circuit breakers or fallback handling when upstream services degrade.
- Return graceful fallback responses instead of raw server errors.
- Add health checks for app, database, and vector store dependencies.
- Maintain runbooks for incident response and recovery.

## 7.5 Testing and Evaluation

### Testing layers

- Unit tests for chunking, prompt building, filtering, and service orchestration
- Integration tests for vector DB, Gemini client wrapper, and API routes
- End-to-end tests for complete HR question-answer scenarios

### Evaluation strategy

- Create a benchmark dataset of representative HR questions.
- Score retrieval relevance and answer correctness.
- Track citation precision and hallucination frequency.
- Re-run evaluations after prompt, chunking, or retriever changes.

## 8. Technology Choices

### Backend

- Python 3.12+
- FastAPI for HTTP API
- Pydantic for schema validation
- `uv` for dependency management, virtual environments, and reproducible installs

### Data and retrieval

- PostgreSQL + `pgvector` or Qdrant
- Optional Redis for caching and lightweight queues

### LLM integration

- Gemini API client wrapper with timeouts, retries, and response normalization

### Deployment

- Docker for containerization
- Kubernetes or managed container platform for production deployment
- CI/CD pipeline for tests, linting, security checks, and deployments

## 9. Implementation Phases

## Phase 1: Foundation

- Initialize project with `uv`
- Set up FastAPI app skeleton
- Add configuration management, logging, and health checks
- Define Pydantic models and API contracts

## Phase 2: Ingestion and Indexing

- Build document loaders
- Implement text cleaning and chunking
- Add embedding generation pipeline
- Integrate vector database and indexing flow

## Phase 3: Chat Retrieval Pipeline

- Implement query preprocessing and metadata filters
- Build retriever and prompt assembly
- Integrate Gemini API for grounded answer generation
- Return citations and fallback responses

## Phase 4: Hardening

- Add authentication and RBAC
- Add rate limiting, tracing, and metrics
- Improve retry, timeout, and error handling paths
- Build evaluation suite and benchmark dataset

## Phase 5: Production Rollout

- Containerize and deploy services
- Set up CI/CD, dashboards, and alerting
- Validate SLA, security posture, and runbooks
- Launch pilot with selected HR and employee groups

## 10. Future Enhancements

- Conversation memory with bounded session context
- Human handoff workflow for unresolved or sensitive HR questions
- Multilingual support for global employees
- Document access controls integrated with enterprise identity systems
- Feedback collection loop for answer quality improvement
- Admin dashboard for ingestion status, retrieval analytics, and failed queries
- Automated document sync from HR knowledge systems
- Reranking and hybrid search improvements
- Policy change detection and scheduled reindexing
- Fine-grained analytics by topic, office, or business unit
- Voice or chat-platform integrations such as Slack or Microsoft Teams

## 11. Final Recommendation

Start with a narrow, high-value HR knowledge scope such as leave policy, benefits FAQ, and onboarding guidance. Build a reliable RAG baseline with strong metadata, citations, and security controls before expanding coverage. The quality of document ingestion, chunking, access control, and evaluation will matter more than model complexity in the first production version.
