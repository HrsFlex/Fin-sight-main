"""
e-Courts Agent for Intelli-Credit.
Searches for litigation records via NJDG (National Judicial Data Grid).
In demo mode, returns realistic simulated litigation data.
"""
from config import IS_DEMO, has_tavily_key, TAVILY_API_KEY, SAMPLE_DATA_DIR
from utils import load_json


def lookup_litigation(company_name: str, promoter_names: list[str] = None) -> dict:
    """
    Look up litigation records for a company and its promoters.
    Returns case details and litigation risk score.
    """
    if IS_DEMO or not has_tavily_key():
        return _get_demo_litigation(company_name)

    return _search_litigation_live(company_name, promoter_names or [])


def _get_demo_litigation(company_name: str = "Bharat Steel Industries") -> dict:
    """Return simulated litigation data."""
    sample = load_json(SAMPLE_DATA_DIR / "sample_company.json")
    lit = sample["litigation_data"]
    
    cname = company_name if company_name else sample["company_name"]
    import hashlib
    seed = int(hashlib.md5(cname.lower().encode()).hexdigest(), 16) % 1000
    
    # Randomize case counts
    total_cases = 5 + (seed % 15)           # 5-19
    pending_cases = seed % 5                # 0-4
    disposed_cases = total_cases - pending_cases
    risk_score = 10 + (seed % 30)           # 10-39
    
    return {
        "company_name": cname,
        "total_cases": total_cases,
        "pending_cases": pending_cases,
        "disposed_cases": disposed_cases,
        "cases": lit["cases"][:max(1, total_cases // 4)], 
        "risk_score": risk_score,
        "risk_level": "LOW" if risk_score < 30 else "MODERATE",
        "criminal_cases": 0,
        "civil_cases": disposed_cases - 1,
        "consumer_cases": 1,
        "total_exposure_cr": 0.5 + (seed % 100) / 10.0,
        "summary": f"A total of {total_cases} litigation cases were found for {cname}, with {pending_cases} currently pending. "
                   f"The majority of cases are civil and consumer-related, with a low overall risk profile.",
        "sources_checked": ["NJDG (njdg.gov.in)", "District Courts", "State Commissions"],
        "method": "demo",
    }


def _search_litigation_live(company_name: str, promoter_names: list[str]) -> dict:
    """Search for litigation data via web search with LLM extraction."""
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY)

        queries = [
            f"{company_name} court case litigation NCLT NCLAT India",
            f"{company_name} DRT debt recovery tribunal case",
            f"{company_name} consumer court case India",
        ]
        for name in promoter_names[:2]:
            queries.append(f"{name} court case criminal arrest FIR India")

        findings = []
        for query in queries:
            try:
                result = client.search(query=query, max_results=3, search_depth="basic")
                for r in result.get("results", []):
                    findings.append({
                        "source": r.get("url", ""),
                        "title": r.get("title", ""),
                        "content": r.get("content", "")[:400],
                    })
            except Exception:
                continue

        from config import has_llm_key, get_llm_client
        if has_llm_key() and findings:
            llm = get_llm_client()
            import json as _json
            prompt = f"""Analyze litigation risk for '{company_name}' from these web search results.

{_json.dumps(findings[:8], indent=1)}

Return ONLY a valid JSON object:
{{
  "total_cases": 0,
  "pending_cases": 0,
  "criminal_cases": 0,
  "civil_cases": 0,
  "drt_cases": 0,
  "nclt_cases": 0,
  "total_exposure_cr": 0.0,
  "risk_score": 25,
  "risk_level": "LOW",
  "key_cases": [],
  "summary": "str"
}}
Base estimates on keywords found. If no cases found, use 0s and LOW risk."""
            try:
                response = llm.invoke(prompt)
                content = response.content
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                data = _json.loads(content.strip())
                return {
                    "company_name": company_name,
                    "total_cases": data.get("total_cases", 0),
                    "pending_cases": data.get("pending_cases", 0),
                    "criminal_cases": data.get("criminal_cases", 0),
                    "civil_cases": data.get("civil_cases", 0),
                    "drt_cases": data.get("drt_cases", 0),
                    "nclt_cases": data.get("nclt_cases", 0),
                    "total_exposure_cr": data.get("total_exposure_cr", 0.0),
                    "risk_score": data.get("risk_score", 25),
                    "risk_level": data.get("risk_level", "LOW"),
                    "key_cases": data.get("key_cases", []),
                    "summary": data.get("summary", f"Litigation analysis completed for {company_name}."),
                    "sources_checked": [f["source"] for f in findings[:5]],
                    "method": "tavily_llm_live",
                }
            except Exception:
                pass

        # Heuristic fallback
        risk_score = 15
        criminal_cases = 0
        for f in findings:
            fl = (f["title"] + " " + f["content"]).lower()
            if any(w in fl for w in ["criminal", "arrest", "fir", "murder", "fraud"]):
                risk_score += 25
                criminal_cases += 1
            elif any(w in fl for w in ["nclt", "nclat", "insolvency", "drt"]):
                risk_score += 15
            elif any(w in fl for w in ["case", "court", "tribunal", "litigation"]):
                risk_score += 5
        risk_score = min(risk_score, 100)

        return {
            "company_name": company_name,
            "total_cases": len([f for f in findings if "case" in (f["title"] + f["content"]).lower()]),
            "pending_cases": 0,
            "criminal_cases": criminal_cases,
            "total_results": len(findings),
            "risk_score": risk_score,
            "risk_level": "LOW" if risk_score < 30 else "MODERATE" if risk_score < 60 else "HIGH",
            "summary": f"Found {len(findings)} web results related to litigation for {company_name}.",
            "sources_checked": [f["source"] for f in findings[:5]],
            "method": "tavily_live",
        }

    except Exception as e:
        result = _get_demo_litigation(company_name)
        result["method"] = "ecourts_fallback"
        result["error"] = str(e)
        return result
