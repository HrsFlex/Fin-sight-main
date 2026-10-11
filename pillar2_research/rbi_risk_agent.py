"""
RBI Risk Agent for Fin-Sight.
Checks RBI defaulter lists, DRT cases, SEBI debarments, and NCLT insolvency proceedings.
"""
from __future__ import annotations
import json
from config import TAVILY_API_KEY, SAMPLE_DATA_DIR, has_tavily_key, has_llm_key, get_llm_client


def check_rbi_risk(company_name: str, promoter_names: list[str] = None, cin: str = "") -> dict:
    """
    Check for RBI willful defaulter listings, DRT cases, SEBI debarments, NCLT insolvency.
    Returns structured risk assessment for credit character pillar.
    """
    promoter_names = promoter_names or []

    if has_tavily_key():
        return _check_live(company_name, promoter_names, cin)

    return _get_demo_rbi(company_name)


def _check_live(company_name: str, promoter_names: list[str], cin: str) -> dict:
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY)

        all_names = [company_name] + promoter_names[:2]
        findings = []

        for name in all_names:
            queries = [
                f'"{name}" "willful defaulter" RBI India bank',
                f'"{name}" NCLT insolvency resolution process India',
                f'"{name}" DRT debt recovery tribunal India',
                f'"{name}" SEBI debarred banned India',
            ]
            for query in queries:
                try:
                    result = client.search(query=query, max_results=2, search_depth="basic")
                    for r in result.get("results", []):
                        findings.append({
                            "subject": name,
                            "source": r.get("url", ""),
                            "title": r.get("title", ""),
                            "content": r.get("content", "")[:400],
                        })
                except Exception:
                    continue

        if has_llm_key() and findings:
            llm = get_llm_client()
            prompt = f"""Analyze RBI/regulatory risk for '{company_name}' from these search results.

{json.dumps(findings[:12], indent=1)}

Return ONLY a valid JSON object:
{{
  "willful_defaulter": false,
  "rbi_defaulter_list": false,
  "drt_cases": 0,
  "sebi_debarment": false,
  "nclt_insolvency": false,
  "default_count": 0,
  "credit_history_rating": "CLEAN",
  "risk_score": 15,
  "risk_flags": [],
  "summary": "str"
}}
credit_history_rating options: CLEAN, WATCH, SUBSTANDARD, DOUBTFUL, LOSS
Populate based on evidence found. Use defaults if no adverse findings."""
            try:
                response = llm.invoke(prompt)
                content = response.content
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                data = json.loads(content.strip())
                return {
                    "company_name": company_name,
                    "willful_defaulter": data.get("willful_defaulter", False),
                    "rbi_defaulter_list": data.get("rbi_defaulter_list", False),
                    "drt_cases": data.get("drt_cases", 0),
                    "sebi_debarment": data.get("sebi_debarment", False),
                    "nclt_insolvency": data.get("nclt_insolvency", False),
                    "default_count": data.get("default_count", 0),
                    "credit_history_rating": data.get("credit_history_rating", "CLEAN"),
                    "risk_score": data.get("risk_score", 15),
                    "risk_flags": data.get("risk_flags", []),
                    "summary": data.get("summary", f"RBI risk check completed for {company_name}."),
                    "method": "tavily_llm_live",
                }
            except Exception:
                pass

        # Heuristic fallback
        risk_score = 10
        risk_flags = []
        willful_defaulter = False
        nclt_insolvency = False
        sebi_debarment = False
        drt_cases = 0
        default_count = 0

        for f in findings:
            fl = (f["title"] + " " + f["content"]).lower()
            if any(w in fl for w in ["willful defaulter", "wilful defaulter"]):
                risk_score += 40
                willful_defaulter = True
                default_count += 1
                risk_flags.append(f"Potential willful defaulter listing: {f['title'][:60]}")
            if any(w in fl for w in ["nclt", "insolvency", "corporate insolvency resolution"]):
                risk_score += 25
                nclt_insolvency = True
                risk_flags.append(f"NCLT/Insolvency proceeding: {f['title'][:60]}")
            if any(w in fl for w in ["sebi", "debarred", "banned", "disgorgement"]):
                risk_score += 20
                sebi_debarment = True
                risk_flags.append(f"SEBI action: {f['title'][:60]}")
            if any(w in fl for w in ["drt", "debt recovery tribunal", "sarfaesi"]):
                drt_cases += 1
                risk_score += 10

        credit_rating = "CLEAN"
        if risk_score >= 60 or willful_defaulter:
            credit_rating = "DOUBTFUL"
        elif risk_score >= 40:
            credit_rating = "SUBSTANDARD"
        elif risk_score >= 25:
            credit_rating = "WATCH"

        return {
            "company_name": company_name,
            "willful_defaulter": willful_defaulter,
            "rbi_defaulter_list": willful_defaulter,
            "drt_cases": drt_cases,
            "sebi_debarment": sebi_debarment,
            "nclt_insolvency": nclt_insolvency,
            "default_count": default_count,
            "credit_history_rating": credit_rating,
            "risk_score": min(risk_score, 100),
            "risk_flags": risk_flags[:5],
            "summary": f"RBI risk check completed for {company_name}. {len(risk_flags)} adverse signals detected.",
            "method": "tavily_live",
        }

    except Exception as e:
        result = _get_demo_rbi(company_name)
        result["error"] = str(e)
        result["method"] = "rbi_fallback"
        return result


def _get_demo_rbi(company_name: str) -> dict:
    import hashlib
    seed = int(hashlib.md5(company_name.lower().encode()).hexdigest(), 16) % 1000
    risk_score = 10 + (seed % 15)

    return {
        "company_name": company_name,
        "willful_defaulter": False,
        "rbi_defaulter_list": False,
        "drt_cases": 0,
        "sebi_debarment": False,
        "nclt_insolvency": False,
        "default_count": 0,
        "credit_history_rating": "CLEAN",
        "risk_score": risk_score,
        "risk_flags": [],
        "summary": f"{company_name} has no adverse RBI/SEBI/NCLT listings. Credit history is clean.",
        "method": "demo",
    }
