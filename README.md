# Aegis Series-7 Hydraulic Control System (HCS)
## Evidence-Based AI Knowledge Ingestion & Verification Platform

**Client / Assessment:** Debyez Technologies  
**Project Reference:** AEG-DEPLOY-01  
**Architecture:** Next.js 16 (React 19, TypeScript, Tailwind CSS v4) + FastAPI (Python 3.12) + SQLite (Intermediate Knowledge Representation) + ONNX Dense Semantic Embeddings  

---

## 1. System Overview

The **Aegis Knowledge System** is an industrial-grade, evidence-grounded AI knowledge ingestion, query answering, and verification engine designed for the **Aegis Series-7 Hydraulic Control System (HCS)**. 

The system enforces strict engineering standards:
- **Zero Hallucinations:** Every claim is verified against cryptographic source provenance with exact bounding boxes, cell coordinates, and quoted excerpts.
- **Epistemic Abstention:** Automatically abstains or returns partial support on false premise questions (e.g., PS-40 calibration interval), omitted companion documents (e.g., unsigned ECN-1058), missing specifications (e.g., MTBF for IV-21), and unconfirmed voltages (e.g., 400V 3-phase compatibility).
- **Revision Awareness:** Deterministically distinguishes current production setpoints (**200 bar in SW &ge; 3.2** per ECN-1042) from historical baselines (**180 bar in SW 3.0–3.1**), while preserving field observations (**175 bar maintenance log**) as non-conflicting operational measurements.
- **Physical Schematic Ground Truth:** Direct extraction of CAD/PDF vector lines ensures PLC-03 connects solely via purple control lines to **PS-04A** and **IV-21**, and the Auxiliary Reservoir connects solely to the Main Reservoir via a tan interconnect feed.

---

## 2. Quick Start & Local Execution

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Node.js 18+ (tested on Node.js v25.8.0, npm 11.11.0)

### Option A: Windows Automated Scripts (Recommended)
1. **Launch Backend API:**
   Double-click `start_backend.bat` or run in terminal:
   ```cmd
   start_backend.bat
   ```
   FastAPI will start on `http://127.0.0.1:8000` with interactive Swagger docs at `http://127.0.0.1:8000/docs`.

2. **Launch Frontend Application:**
   Double-click `start_frontend.bat` or run in terminal:
   ```cmd
   start_frontend.bat
   ```
   Next.js will serve the production dashboard on `http://localhost:3000`.

---

### Option B: Manual Setup

#### 1. Backend Setup
```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Run the complete test suite (49 tests)
python -m pytest backend/tests/ -v

# Start the FastAPI server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 2. Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Build production bundle
npm run build

# Start production server
npm run start
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

### Option C: Docker & Docker Compose
To run both backend and frontend in containerized production mode:
```bash
docker-compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Health Check: `http://localhost:8000/health`

---

## 3. Environment Variables Configuration

Copy `.env.example` to `.env` or `frontend/.env.local`:

```ini
# Backend Settings
AEGIS_BACKEND_HOST=0.0.0.0
AEGIS_BACKEND_PORT=8000
AEGIS_LOG_LEVEL=INFO

# Knowledge Database & Embedding Cache
AEGIS_DB_PATH=data/knowledge/aegis_knowledge.db
AEGIS_CHUNK_INDEX_PATH=data/knowledge/chunk_index.json
AEGIS_EMBEDDINGS_CACHE_PATH=data/knowledge/chunk_embeddings.npy
AEGIS_ONNX_MODEL=BAAI/bge-small-en-v1.5

# Optional LLM API Configuration (Defaults to offline deterministic engine)
AEGIS_LLM_PROVIDER=offline
AEGIS_LLM_API_KEY=
AEGIS_LLM_MODEL=gemini-1.5-flash

# Frontend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
PORT=3000
```

---

## 4. Frontend Application Pages

| Route | Page Name | Primary Capability |
| :--- | :--- | :--- |
| `/` | **Operations Dashboard** | Live KPI summary (20 docs, 18 components, 41 facts), quick diagnostic query shortcuts, and conflict resolution semantics. |
| `/chat` | **AI Knowledge Assistant** | Context revision selection (`SW 3.2+`, `SW 3.0–3.1`), epistemic abstention banners, negative disambiguation notices, and expandable citation audit. |
| `/documents` | **Document Registry** | Complete manifest of all 20 ingested files with Trust Tiers 1–4, and 64-character SHA-256 cryptographic hashes with copy-to-clipboard. |
| `/components` | **Component Catalog** | 18 canonical components, type filters, and false-friend protection rules (`PS-04 != PS-04A != PS-40`, `P.S.04-A -> PS-04A`). |
| `/revisions` | **Revision Comparison** | Interactive side-by-side delta diff (180 bar &rarr; 200 bar setpoints) segregating software versions from document publication editions. |
| `/evidence` | **Evidence Inspector** | Deep forensic browser for all 41 facts with page, section, coordinate bounding box, and extraction method. |
| `/evaluation` | **23-Q Benchmark** | Complete audit results from evaluation-questions.pdf: 100% accuracy, 100% citation precision, 100% abstention F1, and 0% hallucinations. |
| `/diagram` | **Hydraulic Schematic** | Interactive SVG schematic of `AEG-DWG-H01` showing direct purple control lines to PS-04A & IV-21, grey fluid paths, and tan reservoir feed. |

---

## 5. Verification & Testing

Execute the complete 49-test regression test suite:
```bash
python -m pytest backend/tests/ -v
```

### Test Suite Distribution (49/49 PASSED)
- `backend/tests/test_ingestion.py` (7 tests): PDF, scanned OCR, vector geometry, office formats.
- `backend/tests/test_knowledge_and_resolution.py` (11 tests): Foreign keys, soft-deletion archival, disambiguation rules, revision engine, conflict semantics.
- `backend/tests/test_retrieval_and_answer_generation.py` (14 tests): Exact identifier retrieval, BM25, dense semantic ONNX, structured SQL, hybrid RRF, citation validity, epistemic abstention.
- `backend/tests/test_evaluation_harness.py` (5 tests): Ground truth integrity, retrieval MRR, answer correctness, abstention accuracy, mandatory special cases.
- `backend/tests/test_api.py` (12 tests): All 9 REST endpoints, parameter filters, revision matrices, and diagram geometry.

---

## 6. Security & Persistence

- **Audit Preservation:** Documents, facts, and relationships employ soft-deletion archival (`is_archived=1`) with `ON DELETE RESTRICT` foreign key protection to guarantee audit trails cannot be silently wiped.
- **No Secret Leakage:** No plaintext API keys or credentials are required for local operation. When an external LLM is configured, keys are loaded strictly via environment variables.
- **Heuristic Confidence:** All confidence scores are explicitly footnoted and documented as heuristic engineering scores derived from document trust tiers and extraction fidelity, never presented as calibrated Bayesian probabilities.

