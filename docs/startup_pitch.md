# FinSight — Startup Pitch Guide

## The One-Line Pitch

> **FinSight turns 45-day corporate credit appraisals into 4-hour AI-powered decisions — with full explainability and a signed CAM report.**

---

## The Elevator Pitch (60 seconds)

"Every year, Indian banks and NBFCs process 2–4 lakh corporate loan applications. Each one requires a credit analyst to spend 40+ hours reading documents, calling government portals, running financial models, and writing a 40-page report. The average turnaround is 45 days — and even then, 1 in 10 approved loans eventually turns bad.

FinSight changes this. Our AI engine reads the borrower's documents, runs seven independent research agents across MCA filings, court records, news, sector data, and RBI defaulter lists — all in parallel — then produces a fully explainable credit score and a ready-to-sign CAM report. In 4 hours instead of 45 days. At one-tenth the cost.

We're not replacing the credit analyst. We're making one analyst do the work of ten."

---

## The Problem Slide

**Title:** *₹10 lakh crore in bad loans. Most were approved by humans who didn't have enough time.*

- India's banking NPA crisis cost the system ₹10.36 lakh crore at peak (FY2018)
- A typical corporate credit appraisal takes 40+ analyst hours and 30–45 days
- Each appraisal costs ₹2–5 lakh when accounting for analyst, legal, and technical costs
- India has fewer than 50,000 qualified credit analysts — demand far exceeds supply
- Analyst subjectivity: same company, two analysts, 30–40% divergent conclusions

**The root cause isn't analyst incompetence. It's time pressure and information overload.**

---

## The Solution Slide

**Title:** *7 AI agents. 4 hours. One explainable credit decision.*

FinSight is a three-pillar AI pipeline:

**Pillar 1 — Document Intelligence**
Upload PDFs. FinSight reads them, classifies them, and extracts every financial figure — revenue, DSCR, ICR, net worth — using multi-strategy OCR and LLM extraction. Bank statements get behavioral analysis (bounce rate, TOD usage, circular transactions).

**Pillar 2 — Autonomous Research**
7 parallel AI agents research the company across MCA21 filings, NJDG court records, sector outlook, news sentiment, promoter backgrounds, RBI defaulter lists, and live stock/financial data — simultaneously, in minutes.

**Pillar 3 — Credit Decision Engine**
A 22-feature XGBoost model scores the credit application on the industry-standard 5 Cs framework. SHAP explainability shows exactly which factors drove the score. An AI Committee agent triangulates all findings and catches data inconsistencies. One-click generates the full CAM report.

---

## Why Now?

- **RBI's 2023 IT Master Direction** explicitly requires AI-based credit models to be explainable. FinSight uses SHAP — built for compliance.
- **LLM quality crossed a threshold** — GPT-4-class models can now reliably extract structured data from messy Indian documents (something that was impossible 2 years ago).
- **India's credit gap** — MSME credit demand is ₹87 lakh crore; formal supply is ₹24 lakh crore. The gap persists partly because appraisal cost makes small loans uneconomical. FinSight makes SME credit appraisal viable.
- **Tavily + Yahoo Finance + MCA web access** — the external data sources that make research possible are now accessible via API, without needing proprietary data partnerships.

---

## Business Model

| Revenue Stream | Description | Price Point |
|---|---|---|
| SaaS subscription | Monthly seat license for credit teams | ₹15,000–₹5L/month |
| Per-appraisal API | Pay-as-you-go for fintechs and aggregators | ₹500–₹1,500/case |
| Enterprise license | On-premise or private cloud deployment | ₹50L–₹2Cr setup + annual |
| Data insights | Anonymized sector/risk analytics for investors | TBD |

**Unit economics:**
- Cost to run one appraisal (cloud API + compute): ~₹150–₹400
- Revenue per appraisal: ₹500–₹1,500
- Gross margin: 60–75%

---

## Market Size

| Market | TAM | SAM (addressable now) |
|---|---|---|
| India credit analytics software | $520M by 2029 | $80M (BFSI institutions) |
| India BFSI IT spend | $11.5B (2024) | — |
| Global lending decisioning | $32B by 2030 | $200M (South/Southeast Asia) |

**Beachhead:** 50 mid-sized NBFCs and cooperative banks in India currently using Excel-based CAM templates. Each processes 100–500 corporate cases/year. At ₹25,000/month SaaS: **₹15 crore ARR at just 50 customers.**

---

## Competitive Landscape

| Competitor | Strength | FinSight Advantage |
|---|---|---|
| Moody's Analytics CreditLens | Global brand, deep analytics | Not India-specific; expensive; no document OCR |
| Experian/CIBIL Commercial | Bureau data | Only bureau score — no document analysis, no research |
| In-house bank tools | Internal data access | Brittle, not scalable, 2–3 year build cycles |
| Manual process (Excel CAM) | Flexibility | This is the 90% of the market we displace |

**FinSight's moat:** India-specific regulatory context (MCA21, GSTN, NJDG) + document-native AI + explainability compliance + speed to market.

---

## Traction Opportunities

**Ideal first customers:**
- Mid-sized NBFCs (₹500Cr–₹5,000Cr AUM) — smaller compliance burden, faster procurement
- Fintech lenders running MSME credit lines — high volume, cost-sensitive
- Credit guarantee companies (CGTMSE) — need consistent appraisal quality
- Co-lending platforms — need standardized risk formats across partners

**Pilot pitch:**
"Run FinSight on your last 20 approved cases. Compare our output to the actual CAM. We'll show you every red flag we catch that your team flagged — and ones they didn't."

---

## The Founding Team Story (Blend 360 framing)

Blend 360 is a data + AI consultancy embedded inside BFSI, healthcare, and retail enterprises. We've seen the credit appraisal problem from the inside — working alongside risk teams, watching analysts drown in documents. FinSight is the product we built to solve what we kept seeing.

**We are not a startup pretending to understand banking. We are bankers who learned to build AI.**

---

## The Ask (Investor Version)

**Seed round:** ₹3–5 crore

**Use of funds:**
- 40% — Sales & BD: hire 2 enterprise sales reps with BFSI relationships
- 30% — Product: full productization (multi-user, audit logs, regulatory reporting)
- 20% — Compliance: RBI model audit, data residency, ISO 27001
- 10% — Infrastructure: private cloud deployment capability

**18-month milestones:**
- 15 paying pilot customers
- ₹2.5 crore ARR
- Full on-premise deployment option
- Series A raise at ₹20Cr+ ARR trajectory

---

## One-Page Summary

| | |
|---|---|
| **Problem** | Corporate credit appraisal takes 45 days and ₹2–5L per case; subjectivity drives NPAs |
| **Solution** | AI pipeline: document intelligence + 7-agent research + explainable scoring + CAM in 4 hours |
| **Market** | ₹164L crore India bank credit; $520M analytics software market growing 24%/yr |
| **Model** | SaaS ₹15K–₹5L/month + per-appraisal API ₹500–₹1,500 |
| **Moat** | India-specific, explainability-compliant, document-native, no vendor lock-in |
| **Team** | Blend 360 — data + AI consultancy with active BFSI client base |
| **Ask** | ₹3–5Cr seed to productize and close 15 pilot customers |
| **Vision** | Every loan in India — from a ₹10L MSME working capital to a ₹500Cr project finance — appraised by AI, supervised by a human, decided in hours |
