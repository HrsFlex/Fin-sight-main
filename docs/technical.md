# FinSight — Technical Architecture Reference

## What It Is

FinSight is an AI-powered corporate credit appraisal engine. It replaces the manual, analyst-driven process of evaluating a company's creditworthiness with a fully automated three-pillar pipeline — from raw documents to a signed-off Credit Appraisal Memorandum (CAM) — in hours instead of weeks.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT BROWSER                          │
│              FinSight UI  (HTML + JS + Chart.js)                │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼────────────────────────────────────┐
│                    FASTAPI APPLICATION LAYER                     │
│                         api.py  (Python)                         │
│         Session State · File Handling · API Routing             │
└──────┬────────────────────┬──────────────────┬──────────────────┘
       │                    │                  │
       ▼                    ▼                  ▼
┌─────────────┐   ┌─────────────────┐  ┌──────────────────┐
│  PILLAR 1   │   │    PILLAR 2     │  │    PILLAR 3      │
│  Ingestor   │   │    Research     │  │    Engine        │
│             │   │                 │  │                  │
│ OCR Engine  │   │ LangGraph       │  │ Feature Builder  │
│ Classifier  │   │ Orchestrator    │  │ XGBoost Scorer   │
│ LLM Extract │   │ (7 Agents)      │  │ SHAP Explainer   │
│ GST Valid.  │   │                 │  │ Committee Agent  │
│ Bank Stmt   │   │                 │  │ SWOT Generator   │
│ Analyzer    │   │                 │  │ CAM Generator    │
└─────────────┘   └─────────────────┘  └──────────────────┘
       │                    │                  │
       └────────────────────┼──────────────────┘
                            ▼
                ┌───────────────────────┐
                │   PERSISTENCE LAYER   │
                │  SQLite · ChromaDB    │
                │  Local FS (outputs)   │
                └───────────────────────┘
```

---

## Pillar 1 — Document Intelligence

### Components

| Module | Role |
|---|---|
| `ocr_engine.py` | Multi-strategy text extraction: Azure Document Intelligence (if configured), PyMuPDF, pdfplumber, pdf2image+Tesseract |
| `document_classifier.py` | Classifies each document (Annual Report, Bank Statement, GST Return, Sanction Letter, Balance Sheet, P&L, etc.) using filename + content heuristics |
| `llm_extractor.py` | Structured extraction of financial fields (revenue, PAT, DSCR, ICR, net worth) from OCR text using the configured LLM |
| `gst_validator.py` | Cross-validates GST-3B filings against bank credits and declared revenue — flags GSTR-2A vs 3B mismatches |
| `bank_statement_agent.py` | Analyzes bank statement text for behavioral signals: ADB, bounce rate, TOD usage, circular transactions |

### OCR Strategy (priority order)

1. Azure Document Intelligence — highest accuracy for scanned Indian PDFs
2. PyMuPDF — fast native PDF text extraction
3. pdfplumber — table-aware extraction
4. pdf2image + Tesseract — last resort OCR for fully scanned documents

### Document Processing Limits

- Annual reports capped at first 20 pages for speed
- Supports multi-file upload; each file classified independently
- Bank statements automatically routed to behavioral analyzer after OCR

---

## Pillar 2 — Autonomous Research (7 Parallel AI Agents)

### LangGraph Architecture

All agents run in parallel via a `StateGraph` (fan-out from START → all agents → supervisor):

```
         START
           │
    ┌──────┼──────┬──────┬──────┬──────┬──────┐
    ▼      ▼      ▼      ▼      ▼      ▼      ▼
  news   mca  ecourts sector finan- promo- rbi_
 agent  agent  agent  agent  cial   ter   check
                             agent  agent  agent
    │      │      │      │      │      │      │
    └──────┴──────┴──────┴──────┴──────┴──────┘
                           │
                      supervisor
                      (aggregator)
                           │
                          END
```

Falls back to sequential execution if LangGraph is not installed.

### Agent Inventory

| Agent | Data Sources | Output |
|---|---|---|
| **News Agent** | Tavily API → LLM sentiment · Google News RSS (free) | Sentiment score, risk articles, adverse media |
| **MCA Agent** | Tavily → `mca.gov.in`, `zaubacorp.com`, `tofler.in` → LLM extract | Director list, charges, compliance score |
| **e-Courts Agent** | Tavily → NJDG, NCLT, DRT records → LLM extract | Case count by type, exposure, risk level |
| **Sector Agent** | Tavily + LLM · Pollinations AI (free fallback) | Outlook score, regulatory risk, competitors |
| **Financial Agent** | Yahoo Finance (live) · Tavily + LLM · Smart KB | DSCR, ICR, EBITDA margin, live stock quote |
| **Promoter Agent** | Tavily → MCA DIN records, news → LLM | Director disqualifications, adverse history |
| **RBI Risk Agent** | Tavily → RBI defaulter list, DRT, SEBI, NCLT → LLM | Willful defaulter flag, default count |

### Composite Risk Score

```
Composite = (News × 0.25) + (MCA × 0.25) + (Litigation × 0.30) + (Sector × 0.20)
```

Promoter and RBI data feed directly into the `prior_defaults` and `director_disqualifications` features in Pillar 3.

---

## Pillar 3 — Credit Decision Engine

### 5 Cs Framework

| C | Weight | Key Features |
|---|---|---|
| **Character** | 20% | Litigation count, pending cases, news sentiment, MCA compliance, prior defaults, director disqualifications |
| **Capacity** | 25% | DSCR, ICR, Revenue CAGR 3yr, EBITDA margin, current ratio, operating cash flow |
| **Capital** | 20% | D/E ratio, tangible net worth, net worth, promoter equity % |
| **Collateral** | 20% | Asset coverage ratio, LTV %, security type, encumbrance flag |
| **Conditions** | 15% | Industry outlook score, regulatory risk, GST compliance, qualitative risk adjustment |

### Credit Scoring Model

- **Algorithm**: XGBoost Classifier trained on 5,000 synthetic Indian corporate credit samples
- **Features**: 22 features spanning all 5 Cs
- **Output**: Probability score scaled 0–100
- **Explainability**: SHAP TreeExplainer — per-feature Shapley contributions
- **Decision thresholds**:
  - APPROVED: 70–100
  - REFERRED: 50–69
  - REJECTED: 0–49

### Committee Agent

LLM-powered senior credit committee that:
- Triangulates financial numbers against research and GST data
- Identifies hidden risks (circular trading, management quality)
- Produces a final APPROVE / REFER / REJECT verdict with rationale, strengths, concerns, and mitigants

### CAM Report Generation

- Generates a full Credit Appraisal Memorandum as a downloadable DOCX/PDF
- Includes: company profile, financial analysis, 5 Cs scorecard, SWOT, research summary, committee verdict
- SWOT generated by LLM from all pipeline inputs

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, FastAPI, Uvicorn |
| AI Orchestration | LangGraph (StateGraph, parallel agents) |
| LLM Providers | OpenRouter (primary) · OpenAI · Anthropic Claude (configurable) |
| Free LLM Fallback | Pollinations AI (sector agent) |
| Web Search | Tavily API · Google News RSS · Yahoo Finance API |
| ML Scoring | XGBoost · SHAP · NumPy · scikit-learn |
| Document Processing | PyMuPDF · pdfplumber · pdf2image · Azure Document Intelligence |
| Vector Store | ChromaDB (knowledge base) |
| Database | SQLite (session persistence) |
| Object Storage | AWS S3 / Cloudflare R2 (optional large upload) |
| Frontend | Vanilla HTML/CSS/JS · Chart.js · Plotly · html2pdf.js |
| Deployment | Render (primary) · Python venv (local) |

---

## Configuration Modes

| Mode | Condition | Behavior |
|---|---|---|
| **Full Live** | All API keys set | Tavily search + LLM extraction + XGBoost + live quotes |
| **Partial Live** | Some keys set | Available services used; missing ones fall back gracefully |
| **Free Tier** | No paid keys | Google News RSS + Pollinations AI + Yahoo Finance + rule-based scoring |
| **Demo** | `APP_MODE=demo` | All agents return deterministic sample data |

---

## Data Flow (end-to-end)

```
User inputs company + loan details
          ↓
Onboarding API → session created in SQLite
          ↓
User uploads PDFs → OCR → Classify → LLM Extract → GST Validate → Bank Analyze
          ↓
Research API → 7 agents run in parallel → supervisor aggregates
          ↓
Scoring API → feature_builder → XGBoost → SHAP → committee_agent
          ↓
CAM API → SWOT generation → CAM document assembled → download link
```

---

## Key Design Decisions

- **Stateless agents, stateful session**: Each agent is a pure function; the LangGraph state dict carries context. Session state is persisted to SQLite after every mutating API call.
- **Graceful degradation**: Every agent has a free/demo fallback so the pipeline completes even with no API keys.
- **Single-user session model**: The current implementation uses a single default session; extending to multi-user requires per-request session IDs (stubbed in the API).
- **No vendor lock-in**: LLM provider is fully configurable via env vars. Switching from OpenAI to Anthropic or OpenRouter requires one env var change.
