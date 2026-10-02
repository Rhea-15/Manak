# MANAK - Intelligent Indian Standards Procurement

MANAK is an AI-powered compliance engine designed to help procurement teams, vendors, and administrators understand tender specifications, discover applicable Indian Standards (IS), and check compliance automatically. 

---

## 🏗️ System Architecture (The 4 Zones)

MANAK is designed with a highly decoupled, event-driven microservices architecture separated into four logical zones:

1. **Zone 1: External Portals (Ingestion)**
   - Interfaces with government platforms (GeM/CPPP) for tender import/export.
   - Syncs with the BIS Standards Portal and eGazette for real-time QCO notifications.
2. **Zone 2: Presentation Layer (Frontend)**
   - Built on **Next.js 14** and Tailwind CSS.
   - Features rich UI components: Monaco DiffEditor (visual diffs), React Flow (normative standard dependency trees), Recharts (quality score gauges), and TanStack Tables (bulk BOQ parsing).
3. **Zone 3: Application & Security Layer (Backend)**
   - **FastAPI** microservices handling orchestration, document parsing (PyMuPDF, PaddleOCR), and export generation.
   - Role-Based Access Control (RBAC) via **Casbin** and an immutable PostgreSQL audit log.
4. **Zone 4: Intelligence & Data Layer (The Brain)**
   - **Hybrid Search Engine:** Qdrant (dense vectors via `bge-m3`) + BM25 (lexical search) with Reciprocal Rank Fusion (RRF).
   - **Translation Middleware:** IndicTrans2 for handling regional Indian language queries.
   - **Knowledge Graph:** Neo4j for mapping normative and allied standard relationships.
   - **Rules Engine:** Deterministic SQL-based verification for Quality Control Orders (QCO) and ISI marks.

---

## 🚀 Implementation Status

### ✅ What is Done
* **Core Architecture & Ingestion:** FastAPI gateway, Next.js frontend, and multi-format document parsing (PyMuPDF with basic PaddleOCR fallback).
* **Hybrid Search Engine:** Qdrant vector database and BM25 lexical index functioning with RRF.
* **Graph Knowledge Base:** Neo4j integration mapping IS relationships, synchronized with PostgreSQL.
* **RBAC & Governance:** Casbin-based role management (Admin, Manager, Executive) with immutable audit logging.
* **Multilingual Support:** IndicTrans2 pipeline configured for regional language translation prior to vector search.

### ⏳ What is Pending (Development Roadmap)
* **Asynchronous Pipeline:** Implement Celery task queues for handling large-scale PDF and PaddleOCR extractions without blocking API threads.
* **Advanced LLM Integration:** Wire up the constrained LLM (using Pydantic/Instructor guardrails) to generate 3-bullet executive summaries for standard version diffs.
* **Production Scoring Engine:** Replace the current `mock_score` function with the fully deterministic mathematical Tender Quality Score engine.
* **International Mapping:** Populate the Neo4j graph and Qdrant database with ISO/IEC/ASTM to Indian Standard cross-mapping vectors.

---

## 🗄️ Backend Data Strategy

The backend relies on a multi-model data architecture:
* **PostgreSQL (Relational):** Manages Standards, Versions, Amendments, QCO Requirements, and Casbin policies.
* **Neo4j (Graph):** Stores standard dependency nodes (Normative References, Allied Standards).
* **Qdrant (Vector):** Stores `bge-m3` document embeddings for semantic search.

**Current Seed Data:** The repository uses development seed scripts (`seed_relations.py`, `bulk_seed.py`, `boost_data.py`, `seed_pipeline.py`) injecting a subset of standards (e.g., IS 456, IS 10262). 
*Note: For production readiness, the system requires bulk ingestion of the official BIS catalog and live eGazette notifications.*

---

## ⚙️ Environment Configuration (`.env`)

Before running the system, configure the following environment variables:

**Databases & Storage:**
* `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
* `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`, `MINIO_ENDPOINT`
* `REDIS_URL`
* `NEO4J_AUTH` (e.g., `neo4j/password`)

**AI & Search Config:**
* `QDRANT_HOST`, `QDRANT_PORT`
* `EMBEDDING_MODEL` (Default: `BAAI/bge-m3`)
* `INDICTRANS2_MODEL` (Default: `ai4bharat/indic-trans-v2-all-gpu`)

**API Routing:**
* `BACKEND_HOST`, `BACKEND_PORT`
* `FRONTEND_URL` (For CORS, e.g., `http://localhost:3000` or `https://manak.gov.in`)

---

## 💻 Local Development Setup

To run the application locally across terminals:

### Step 1: Start Docker Infrastructure Containers
```bash
docker-compose up -d postgres neo4j minio qdrant redis
```

### Step 2: Initialize Databases & Seed Data
Run from the root directory inside your Python virtual environment:
```bash
python -m src.backend.db_init
python src/db_graph/seed_relations.py
python src/db_graph/bulk_seed.py
python -m src.ai_search.seed_pipeline
```

### Step 3: Start Services Across Terminals

* **Terminal 1: AI Search Microservice (Port 8001)**
  ```bash
  uvicorn src.ai_search.main:app --host 0.0.0.0 --port 8001 --reload
  ```
  
* **Terminal 2: Core Orchestration Gateway (Port 8000)**
  ```bash
  uvicorn src.orchestration.main:app --host 0.0.0.0 --port 8000 --reload
  ```

* **Terminal 3: Next.js Frontend (Port 3000)**
  ```bash
  cd src/frontend
  npm install
  npm run dev
  ```
---

## 🌐 Production Deployment Guide

Transitioning from `localhost` to a production environment requires containerizing the application services, establishing network isolation, and configuring a reverse proxy.

### 1. Architectural Changes for Production
* **Eliminate `localhost`:** Replace all `localhost` references in your connection strings with Docker service names (e.g., `postgres:5432`, `neo4j:7687`, `qdrant:6333`).
* **Close Exposed Database Ports:** In production, **do not** bind database ports (5432, 7687, 6333, 6379, 9000) to the host machine. Keep them completely isolated inside an internal Docker network (e.g., `backend_net`).
* **Nginx Reverse Proxy:** Route all browser traffic through port `80`/`443` using Nginx. Configure Nginx to pass `/` requests to the Next.js container and `/api/` (or `/documents/`, `/review/`, etc.) requests to the FastAPI container. This completely solves CORS and browser-side `localhost` resolution errors.

### 2. Handling AI Models
* To prevent multi-gigabyte downloads during every container restart, pre-bake model weights (`BAAI/bge-m3`, `en_core_web_sm`) directly into the Docker image during the build phase, or mount an external cloud volume (e.g., AWS EFS).
* Deploy on GPU-enabled instances (with CUDA/NVIDIA Container Toolkit) or utilize quantized models (ONNX Runtime) for latency-sensitive CPU environments.

### 3. Production Deployment Commands
Using the consolidated `docker-compose.prod.yml`:
```bash
# 1. Spin up the entire stack (Proxy, Frontend, Backend, Databases)
docker compose -f docker-compose.prod.yml up -d --build

# 2. Run initial database migrations and seed scripts inside the backend container
docker compose -f docker-compose.prod.yml exec backend python -m src.backend.db_init
docker compose -f docker-compose.prod.yml exec backend python src/db_graph/seed_relations.py
docker compose -f docker-compose.prod.yml exec backend python src/db_graph/bulk_seed.py
docker compose -f docker-compose.prod.yml exec backend python -m src.ai_search.seed_pipeline

# 3. Verify health
curl http://localhost/health
```

---

## 🧪 Testing & CI/CD Workflow

**Continuous Integration:**
The repository enforces a strict CI pipeline via GitHub Actions. Every push and pull request automatically triggers:
1. **Ruff** for Python linting.
2. **ESLint** for Next.js linting.
3. **Pytest** for backend unit/integration tests.
4. **CodeRabbit AI** automated code reviews for security vulnerabilities, logic bugs, and React anti-patterns.

**Running Tests Locally:**
The test suite utilizes custom markers to isolate component testing:
* **Run entire suite:** `pytest tests/ -v`
* **Skip slow integration tests:** `pytest -m "not slow"`
* **Run specific modules:** `pytest -m search_ready` or `pytest -m backend_ready`

---

## 📖 API Documentation
Once the FastAPI backend is active, interactive documentation is auto-generated and accessible at:
* **Swagger UI:** `/docs` (e.g., `http://localhost:8000/docs`)
* **ReDoc:** `/redoc` (e.g., `http://localhost:8000/redoc`)
