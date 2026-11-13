# Concepts guide: where each idea lives in this project

Read this file next to the code. Each section names the concept, gives
an everyday analogy, and points to the file where it is used.

---

## 1. FastAPI: the web framework
**What:** A Python framework for building APIs (like Express for Node).
**Analogy:** A building with doors (routes). Each door has a sign (URL + method).
Behind it, a receptionist (controller) passes your request to an expert (service).

| Layer | Job | Files |
|---|---|---|
| Route | URL + method, input/output types | `backend/app/routes/*.py` |
| Controller | HTTP concerns: errors → status codes | `backend/app/controllers/*.py` |
| Service | Pure business logic, no HTTP | `backend/app/services/**` |
| Middleware | Runs around *every* request | `backend/app/middleware/timing.py` |
| Entry point | Wires it all together | `backend/app/main.py` |

Key ideas to look for:
- `@router.get(...)` turns a function into an endpoint.
- `Depends(get_db)` is **dependency injection**: FastAPI hands each request a DB session and closes it afterwards.
- `/docs` is interactive API documentation, generated automatically from your type hints.

## 2. Pydantic: data validation with type hints
**What:** You declare a class with typed fields; Pydantic checks real data against it.
**Analogy:** A delivery box with labelled slots. A wrong item doesn't fit, so it is rejected at the door.

Used in three places:
1. **Settings:** `backend/app/config/settings.py` (`BaseSettings` reads `.env` and validates it).
2. **API inputs/outputs:** `backend/app/schemas/*.py` (`ChatRequest` rejects an empty question with 422).
3. **Validating LLM output:** `RouteDecision` in `backend/app/services/assistant/assistant_service.py`
   uses `Literal[...]` so the LLM can only pick allowed tool names.

## 3. SQLAlchemy and the ORM
**What:** SQLAlchemy is the Python ↔ SQL toolkit. **ORM** = Object-Relational Mapper:
a table becomes a class and a row becomes an object.
**Analogy:** Mongoose for SQL. You write `select(Merchant)` instead of `SELECT * FROM merchants`.

- **Engine / Session / Base:** `backend/app/config/database.py`
  (engine = phone line, session = one call, Base = parent of every table class).
- **Models (tables):** `backend/app/models/merchant.py`, `transaction.py`.
  Shows primary key, foreign key, `relationship()` and `Numeric` for money.
- **Writing rows:** `backend/app/services/ingestion/seed_service.py` (`add_all` then `commit`).
- **Aggregate queries:** `backend/app/services/analytics/analytics_service.py`
  (`func.count`, `func.sum`, `case`, `join`, `group_by`). The database does the math.

## 4. LLM (Large Language Model) and Ollama
**What:** A model that predicts the next words given a prompt. It is good with language
but doesn't know your private data and is weak at arithmetic.
**Ollama** runs open models (here **Llama 3.2 3B**) locally behind an HTTP API.

- `backend/app/services/assistant/ollama_client.py`: an LLM call is just an HTTP POST
  with `messages` (system / user roles). `temperature: 0` makes it repeatable; `format: json`
  forces JSON output.

## 5. Sentence-Transformers and embeddings
**What:** An embedding model turns text into a vector (384 numbers for `all-MiniLM-L6-v2`).
Similar meaning gives nearby vectors, even with no shared words.
**Analogy:** GPS coordinates on a "meaning map".

- `backend/app/services/rag/dense.py`: encodes every chunk once, then scores a query
  by **cosine similarity** (a dot product of normalised vectors).

## 6. RAG (Retrieval-Augmented Generation)
**What:** Retrieve relevant passages, Augment the prompt with them, and the LLM Generates an answer.
**Analogy:** An open-book exam. We hand the model the right pages.

| Step | File |
|---|---|
| Chunk documents (one `##` section = one chunk) | `services/ingestion/document_loader.py` |
| Keyword retrieval: **BM25** | `services/rag/bm25.py` |
| Meaning retrieval: **embeddings** | `services/rag/dense.py` |
| Fuse both: **RRF** | `services/rag/search_service.py` |
| Augment + generate | `services/assistant/assistant_service.py` |

- **BM25** wins on exact codes (`BANK_TIMEOUT`).
- **Dense** wins on paraphrases ("payment took too long to confirm").
- **RRF** `score = Σ 1/(60 + rank)` combines them using ranks only, so the different
  score scales don't matter.

Try it: `GET /api/search?q=Why might a payment take too long to receive confirmation?`
shows all three rankings side by side.

## 7. The AI assistant (tool routing)
`backend/app/services/assistant/assistant_service.py`
1. **Route:** LLM call #1 returns JSON: `analytics`, `documents` or `both` (plus which metric).
2. **Gather:** normal Python runs the SQL query and/or the RAG search.
3. **Answer:** LLM call #2 writes the reply using only that context, with citations.

If the LLM returns invalid JSON, Pydantic catches it and a keyword-based backup router is used.

## 8. React frontend
- `frontend/src/api.js`: every backend call in one place.
- `frontend/src/App.jsx`: the "backend connected" badge from `/health` and the tabs.
- `frontend/src/pages/Dashboard.jsx`: KPI cards and Recharts bar charts.
- `frontend/src/pages/Chat.jsx`: chat that shows the route plus the evidence used.
- `frontend/vite.config.js`: dev proxy (`/api` goes to `localhost:8000`).
- `frontend/dist/assets/*`: **generated** by `npm run build` (all of `src/` bundled into one
  `.js` and one `.css`). Never edit them. They are git-ignored, and FastAPI serves them in production.
