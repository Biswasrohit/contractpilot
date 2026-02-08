# ContractPilot

AI-powered contract reviewer. Upload any contract — even scanned paper documents — and get instant risk analysis with plain-English summaries and a downloadable PDF report.

## Architecture

```
Browser → Next.js (port 3000) → Python FastAPI (port 8000)
            │                        │
        Flowglad billing        Dedalus ADK agent
        Convex (real-time)         ├── MCP: DAuth (security)
                                   ├── MCP: pdf-parse (doc parsing)
                                   ├── MCP: brave-search (broad search)
                                   ├── MCP: exa-mcp (deep search)
                                   ├── MCP: context7 (template comparison)
                                   ├── K2 Think via Vultr (clause analysis)
                                   ├── Vultr RAG (legal knowledge base)
                                   └── Google Vision OCR (scanned docs)
```

### Pipeline

1. **Phase 1** — Local classify + extract (instant)
2. **Phase 2** — Parallel: RAG + K2 Think per clause + Exa MCP legal research (~35s)
3. **Phase 3** — Dedalus summary enriched with Exa context (single LLM call, ~15s)
4. **Phase 4** — Save results to Convex + generate PDF report

## Prerequisites

- **Node.js** >= 18
- **Python** >= 3.11
- **npm**
- API keys for: Dedalus, Vultr, Google Cloud Vision, Flowglad, Convex

## Quick Start (Docker)

The fastest way to run ContractPilot. Requires [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/).

### 1. Clone

```bash
git clone <repo-url> && cd contractpilot
```

### 2. Configure environment

Create `backend/.env`:

```
DEDALUS_API_KEY=sk-ded-...
DEDALUS_AS_URL=https://as.dedaluslabs.ai
VULTR_INFERENCE_API_KEY=your-vultr-key
VULTR_LEGAL_COLLECTION_ID=your-collection-id
CONVEX_URL=https://your-project.convex.cloud
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json
FRONTEND_URL=http://localhost:3000
```

Create `frontend/.env.local`:

```
NEXT_PUBLIC_CONVEX_URL=https://your-project.convex.cloud
FLOWGLAD_SECRET_KEY=sk_test_...
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
CONVEX_DEPLOYMENT=dev:your-project
```

Place your `google-credentials.json` in `backend/`.

### 3. Build and run

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend health: http://localhost:8000/health

### 4. Seed legal knowledge base (one-time)

```bash
docker compose exec backend python seed_vultr_rag.py
```

## Quick Start (Local Development)

### 1. Frontend setup

```bash
cd frontend
npm install
```

Copy `.env.local` and fill in your keys:

```
NEXT_PUBLIC_CONVEX_URL=https://your-project.convex.cloud
FLOWGLAD_SECRET_KEY=sk_test_...
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### 2. Convex setup

```bash
cd frontend
npx convex dev
```

This will prompt you to create a Convex project and deploy the schema. Keep this running — it watches for changes.

### 3. Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Copy `.env` and fill in your keys:

```
DEDALUS_API_KEY=sk-ded-...
DEDALUS_AS_URL=https://as.dedaluslabs.ai
VULTR_INFERENCE_API_KEY=your-vultr-key
VULTR_LEGAL_COLLECTION_ID=your-collection-id
CONVEX_URL=https://your-project.convex.cloud
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json
FRONTEND_URL=http://localhost:3000
```

### 4. Seed legal knowledge base (one-time)

```bash
cd backend
python seed_vultr_rag.py
```

Downloads CUAD + Legal Clauses datasets from Kaggle and uploads to Vultr vector store.

### 5. Run the app

Open three terminals:

```bash
# Terminal 1 — Frontend
cd frontend
npm run dev
# → http://localhost:3000

# Terminal 2 — Convex
cd frontend
npx convex dev
# → watches for schema changes

# Terminal 3 — Backend
cd backend
source .venv/bin/activate
uvicorn main:app --reload --port 8000
# → http://localhost:8000
```

### 6. Verify

- Frontend: http://localhost:3000
- Backend health: http://localhost:8000/health → `{"status": "ok"}`
- Convex dashboard: shown in terminal output

## Project Structure

```
contractpilot/
├── frontend/                # Next.js 14 (App Router + Tailwind)
│   ├── src/app/             # Pages and API routes
│   ├── src/components/      # React components
│   ├── Dockerfile           # Production container
│   └── package.json
├── frontend/convex/         # Convex schema + queries/mutations
├── backend/                 # Python FastAPI
│   ├── main.py              # FastAPI app + routes
│   ├── agent.py             # Dedalus ADK agent orchestration (hybrid pipeline)
│   ├── exa_search.py        # Exa MCP search integration
│   ├── tools.py             # Custom tool functions
│   ├── k2_client.py         # K2 Think via Vultr Inference
│   ├── vultr_rag.py         # Vultr RAG legal knowledge queries
│   ├── seed_vultr_rag.py    # One-time Kaggle data seeder
│   ├── report_generator.py  # PDF report (WeasyPrint)
│   ├── ocr.py               # Google Vision OCR
│   ├── prompts.py           # System prompts
│   ├── Dockerfile           # Production container
│   └── pyproject.toml
├── docker-compose.yml       # Full-stack orchestration
└── README.md
```

## Stack

| Category | Tools |
|----------|-------|
| MCPs (5) | DAuth + pdf-parse + brave-search + exa-mcp + context7 |
| AI Models (3) | K2 Think (Vultr) + Google Vision OCR + Vultr RAG |
| Billing | Flowglad — first review free, then $2.99/contract |
| Database | Convex — real-time, frontend + backend read/write |
| Frontend | Next.js 14 + Tailwind CSS |
| Backend | Python FastAPI + Dedalus ADK |

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|----------|-------------|
| `DEDALUS_API_KEY` | Dedalus Labs API key |
| `DEDALUS_AS_URL` | Dedalus AS endpoint |
| `VULTR_INFERENCE_API_KEY` | Vultr Serverless Inference API key |
| `VULTR_LEGAL_COLLECTION_ID` | Vultr RAG collection ID |
| `CONVEX_URL` | Convex deployment URL |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Google Cloud credentials JSON |
| `FRONTEND_URL` | Frontend URL for CORS |

### Frontend (`frontend/.env.local`)

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_CONVEX_URL` | Convex deployment URL (public) |
| `FLOWGLAD_SECRET_KEY` | Flowglad billing secret key |
| `NEXT_PUBLIC_BACKEND_URL` | Python backend URL |
| `CONVEX_DEPLOYMENT` | Convex deployment identifier |
