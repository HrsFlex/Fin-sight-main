# FinSight — Problem, Solution & Business Impact

## The Problem: Corporate Credit Appraisal Is Broken

### What Credit Appraisal Is

When a company applies for a business loan from a bank or NBFC, it goes through a **credit appraisal** — a structured evaluation of the borrower's ability and willingness to repay. This requires:

- Collecting and reading dozens of documents (annual reports, bank statements, GST returns, legal notices)
- Researching the company's reputation, litigation history, sector outlook
- Running financial models (DSCR, ICR, D/E ratio, CAGR)
- Writing a Credit Appraisal Memorandum (CAM) — a 30–60 page document summarizing findings
- Presenting to a credit committee for approval

### The Pain Points

**1. It takes too long.**

A typical corporate credit appraisal takes **30 to 60 days** from application to sanction. This is not processing time — it is analyst time. A skilled credit analyst handles 3–5 proposals simultaneously, manually reading hundreds of pages per case.

**2. It costs too much.**

A mid-sized bank employs **500–2,000 credit analysts** at ₹8–25L CTC per year. For large corporate accounts, the end-to-end cost per appraisal (analyst time + legal + technical) is **₹2–5 lakh per case**. For SME lending, it often costs more to appraise than the loan earns.

**3. It is inconsistent.**

Two analysts at the same bank looking at the same company reach different conclusions 30–40% of the time, according to internal audit findings across Indian public sector banks. This subjectivity drives NPA (Non-Performing Asset) cycles.

**4. Talent is scarce and expensive.**

India has fewer than 50,000 qualified corporate credit analysts. Banks compete for the same talent pool. Training a new analyst takes 18–24 months before they can independently close a case.

**5. The NPA crisis is a consequence.**

Indian banking sector Gross NPAs peaked at ₹10.36 lakh crore in FY2018 (11.2% of advances). Despite improvement, stressed assets remain a structural problem. A significant portion traces back to poor quality initial credit appraisals — where early warning signals in financial data, litigation records, or promoter backgrounds were missed.

### The Scale of the Market

| Segment | Size | Growth |
|---|---|---|
| India bank credit outstanding | ₹164 lakh crore (FY2024) | 16% YoY |
| NBFC credit book | ₹38 lakh crore | 18% YoY |
| Corporate & MSME credit | ~₹60 lakh crore | — |
| Annual new corporate loan appraisals (est.) | 2–4 lakh cases/year | — |
| Credit analytics software market (India) | $180M (2024) → $520M (2029) | 24% CAGR |
| Global lending decisioning software | $12.8B (2024) → $32B (2030) | 16% CAGR |

---

## The Solution: FinSight

FinSight compresses a 30–60 day process into **2–4 hours** with higher consistency and full auditability.

### How It Solves Each Problem

| Problem | FinSight Solution |
|---|---|
| Slow turnaround | Fully automated pipeline: OCR → 7 parallel AI agents → XGBoost scoring → CAM in hours |
| High cost | Analyst reviews AI-generated report instead of building from scratch — 80–90% time reduction |
| Inconsistency | Deterministic 5 Cs framework + XGBoost model — same inputs always produce same analysis |
| Talent scarcity | One analyst supervises 10× more cases with AI doing the heavy lifting |
| NPA risk | Catches early warning signals (promoter background, RBI defaulter check, GST cross-validation) that manual review often misses under time pressure |

### What FinSight Delivers

1. **Automated document extraction** — OCR + LLM reads annual reports, bank statements, GST returns, extracts financial figures into structured JSON
2. **7-agent research pipeline** — parallel AI research on MCA filings, litigation history, sector outlook, promoter backgrounds, RBI defaulter lists, news sentiment, live financials
3. **Explainable credit score** — XGBoost model with SHAP waterfall showing exactly which factors drove the score
4. **AI Committee verdict** — LLM-powered committee synthesizes all data and flags data inconsistencies (e.g., declared revenue ≠ bank credits ≠ GST filings)
5. **One-click CAM report** — full Credit Appraisal Memorandum ready for committee review, not a blank template

---

## Business Impact

### For Banks and NBFCs

**Cost reduction:**
- Manual CAM preparation: ~40 analyst-hours per case
- FinSight-assisted: ~4 hours (analyst reviews, edits, approves)
- **90% reduction in analyst time per case**
- At ₹15L CTC (₹720/hr), saving 36 hours = **₹26,000 saved per appraisal**
- At 500 cases/year: **₹1.3 crore/year in analyst cost savings per branch**

**Speed to sanction:**
- Manual: 30–60 days average
- FinSight: 2–4 hours for analysis; 2–5 days for legal/technical verification
- **12–15× faster time-to-sanction**

**Portfolio quality:**
- Standardized 5 Cs scoring reduces subjective variance
- Promoter background + RBI defaulter check catches red flags before disbursement
- GST cross-validation detects revenue inflation (common in NPA cases)
- Estimated **15–25% improvement in early-warning NPA detection rate**

**Capacity multiplier:**
- A team of 10 analysts currently handles ~300 cases/year
- With FinSight: same team handles **2,000–3,000 cases/year**
- Enables banks to expand SME lending (currently underserved due to high appraisal cost)

### For the Borrower

- Faster decision — no waiting 45 days for a yes or no
- Transparent — the SHAP waterfall shows exactly what worked against them
- Consistent — reapplying 6 months later gets the same framework applied

---

## Potential Revenue Model

### SaaS / API Pricing

| Tier | Target | Price | Use |
|---|---|---|---|
| Starter | Small NBFCs, fintechs | ₹15,000/month | Up to 50 appraisals/month |
| Professional | Mid-sized banks, cooperative banks | ₹50,000/month | Up to 300 appraisals/month |
| Enterprise | Large PSU/private banks | ₹2–5L/month + setup | Unlimited, on-premise option |
| Per-appraisal API | Fintechs, loan aggregators | ₹500–₹1,500/appraisal | Pay-as-you-go |

### Revenue Projections (Conservative)

| Year | Customers | ARR |
|---|---|---|
| Year 1 | 5 NBFCs + 2 banks (Starter/Pro) | ₹1.2 crore |
| Year 2 | 20 NBFCs + 8 banks + API partners | ₹6 crore |
| Year 3 | 50 institutions + 3 enterprise | ₹22 crore |

### Comparable Benchmarks

- **Experian / CIBIL** commercial: $150–300 per bureau pull (India mid-enterprise)
- **Moody's Analytics CreditLens**: $50,000–$200,000/year per institution
- **Bureau of Business Analytics (global)**: credit SaaS typically commands 3–5% of prevented NPA losses as annual contract value

---

## The Unfair Advantages

1. **India-specific** — built for Indian regulatory context (MCA21, GSTN, NJDG, RBI defaulter list). Global vendors struggle here.
2. **No vendor lock-in** — works with OpenAI, Anthropic, or free models. Runs fully local if needed.
3. **Explainability by design** — SHAP output satisfies RBI's model explainability requirements for AI-assisted lending (RBI Master Direction on IT 2023).
4. **Document-native** — reads actual uploaded PDFs, not just structured data feeds. Captures the messy reality of Indian corporate filings.
5. **Blend 360 credibility** — built by a data + AI consulting firm already embedded in BFSI clients.
