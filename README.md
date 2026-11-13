# Merchant Business Intelligence

AI-powered full-stack application for UPI merchant transaction analytics and business intelligence.

## Components
- **Analytics Engine**: Python, Pandas, SQLAlchemy, PostgreSQL
- **RAG Engine**: BM25 + dense retrieval (Sentence-Transformers) + Reciprocal Rank Fusion
- **AI Assistant**: local LLM via Ollama (Llama 3.2 3B), routes questions to analytics/RAG tools

## Stack
React (JavaScript, Vite, Recharts) · FastAPI · PostgreSQL · Pandas/NumPy · SQLAlchemy · Ollama

New to these concepts? Read **[docs/CONCEPTS.md](docs/CONCEPTS.md)**.

## Project structure
```
backend/app/
  main.py          entry point (wires everything)
  config/          settings (.env) + database connection
  models/          SQLAlchemy ORM tables (Merchant, Transaction)
  schemas/         Pydantic request/response shapes
  routes/          URL endpoints
  controllers/     HTTP error handling, calls services
  services/
    ingestion/     CSV → PostgreSQL, documents → chunks
    analytics/     totals, success rates, top merchants, failure reasons
    rag/           BM25, embeddings, RRF hybrid search
    assistant/     Ollama client + question router
  middleware/      request timing log
  utils/           logger, tokenizer
frontend/src/      React: Dashboard + AI Assistant pages
data/              sample CSVs + policy documents
```

## Run locally (Windows)

**1. Database (once)**: in PowerShell:
```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres
```
```sql
CREATE USER mbi_app WITH PASSWORD 'YourPassword123';
CREATE DATABASE merchant_bi OWNER mbi_app;
\q
```

**2. Backend**
```powershell
cd backend
copy .env.example .env        # then put your password in DATABASE_URL
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs: http://localhost:8000/docs

**3. Model (once)**
```powershell
ollama pull llama3.2:3b
```

**4. Frontend**
```powershell
cd frontend
npm install
npm run dev
```
Open http://localhost:5173 and click **Load / reload sample data** (or `POST /api/seed`).

## API
| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | DB + Ollama status |
| POST | `/api/seed` | Load CSVs into PostgreSQL (safe to re-run) |
| GET | `/api/analytics/summary` | Totals, volume, success rate |
| GET | `/api/analytics/merchant-success-rates` | Per-merchant success rate |
| GET | `/api/analytics/top-merchants?limit=5` | Ranked by successful volume |
| GET | `/api/analytics/failure-reasons` | Failed payments by reason |
| GET | `/api/search?q=...&top_k=3` | Compare BM25 vs dense vs RRF |
| POST | `/api/chat` | `{"question": "..."}` → AI answer + evidence |

## Deploy (one server, no Docker)
Build the React app once. FastAPI then serves it alongside the API on port 8000.
```powershell
cd frontend
npm run build                 # creates frontend/dist (generated files, git-ignored)
cd ..\backend
.venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Open http://localhost:8000. PostgreSQL and Ollama must be running on the same machine,
with the database URL set in `backend/.env`.
