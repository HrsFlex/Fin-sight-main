"""
MCA Agent for Intelli-Credit.
Looks up Ministry of Corporate Affairs (MCA21) data for a company.
In demo mode, returns realistic simulated MCA data.
In live mode, performs web search for publicly available MCA filings.
"""
from config import IS_DEMO, has_tavily_key, TAVILY_API_KEY, SAMPLE_DATA_DIR
from utils import load_json


def lookup_mca_data(company_name: str, cin: str = "") -> dict:
    """
    Look up MCA21 data for a company.
    Returns director info, charges, compliance status.
    """
    if IS_DEMO or not has_tavily_key():
        return _get_demo_mca(company_name, cin)

    return _search_mca_live(company_name, cin)


def _get_demo_mca(company_name: str, cin: str) -> dict:
    """Return simulated MCA data."""
    from utils import load_json
    sample = load_json(SAMPLE_DATA_DIR / "sample_company.json")
    mca = sample["mca_data"]
    promoters = sample["promoters"]
    cname = company_name if company_name else sample["company_name"]
    
    import hashlib
    seed = int(hashlib.md5(cname.lower().encode()).hexdigest(), 16) % 1000
    
    # Randomize numeric metrics based on seed
    comp_score = 90 + (seed % 10) # 90-99
    reg_charges = (seed % 50) + 10 # 10-59
    open_charges = seed % 4        # 0-3
    sat_charges = reg_charges - open_charges
    risk_score = 10 + (seed % 15)  # 10-24

    return {
        "company_name": cname,
        "cin": cin or sample["cin"],
        "incorporation_date": sample["incorporation_date"],
        "registered_office": sample["registered_office"],
        "directors": [
            {
                "name": p["name"],
                "din": p["din"],
                "designation": p["designation"],
                "status": "Active",
                "other_directorships": 1 if i == 0 else 0,
                "disqualified": False,
            }
            for i, p in enumerate(promoters)
        ],
        "charges": {
            "total_registered": reg_charges,
            "satisfied": sat_charges,
            "open": open_charges,
            "details": mca["charges_detail"][:max(1, open_charges)],
        },
        "compliance": {
            "annual_returns_filed": mca["annual_returns_filed"],
            "last_agm_date": mca["last_agm_date"],
            "roc_notices": mca["roc_notices"],
            "compliance_score": comp_score,
        },
        "risk_score": risk_score,
        "risk_flags": [],
        "summary": f"MCA records for {cname} show {comp_score}% compliance. There are {open_charges} open charges and {sat_charges} satisfied charges recorded. "
                   "Digital filings are up to date with no pending ROC notices.",
        "method": "demo",
    }


def _search_mca_live(company_name: str, cin: str) -> dict:
    """Search for MCA data via web search with LLM extraction."""
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY)

        queries = [
            f"{company_name} MCA21 company details directors charges India site:mca.gov.in OR site:zaubacorp.com OR site:tofler.in",
            f"{cin} MCA company registration" if cin else f"{company_name} CIN director DIN India company registration",
            f"{company_name} ROC filing annual return compliance",
        ]

        findings = []
        for query in queries:
            try:
                result = client.search(query=query, max_results=3, search_depth="basic")
                for r in result.get("results", []):
                    findings.append(f"Source: {r.get('url')}\n{r.get('content', '')[:500]}")
            except Exception:
                continue

        if not findings:
            raise Exception("No MCA search results found")

        from config import has_llm_key, get_llm_client
        if has_llm_key():
            llm = get_llm_client()
            prompt = f"""Extract MCA21 data for '{company_name}' from these web search results.

{chr(10).join(findings[:6])}

Return ONLY a valid JSON object:
{{
  "directors": [{{"name": "str", "din": "str", "designation": "str", "disqualified": false}}],
  "open_charges": 0,
  "satisfied_charges": 0,
  "compliance_score": 70,
  "roc_notices": 0,
  "annual_return_filed": true,
  "risk_flags": [],
  "risk_score": 35,
  "summary": "str"
}}
If data is unavailable for a field, use sensible defaults (0 for counts, 70 for compliance_score, false for booleans)."""
            try:
                import json as _json
                response = llm.invoke(prompt)
                content = response.content
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                data = _json.loads(content.strip())
                return {
                    "company_name": company_name,
                    "cin": cin or "Not available",
                    "directors": data.get("directors", []),
                    "charges": {
                        "open": data.get("open_charges", 0),
                        "satisfied": data.get("satisfied_charges", 0),
                        "total_registered": data.get("open_charges", 0) + data.get("satisfied_charges", 0),
                    },
                    "compliance": {
                        "compliance_score": data.get("compliance_score", 70),
                        "roc_notices": data.get("roc_notices", 0),
                        "annual_returns_filed": data.get("annual_return_filed", True),
                    },
                    "risk_score": data.get("risk_score", 35),
                    "risk_flags": data.get("risk_flags", []),
                    "summary": data.get("summary", f"MCA data extracted from web search for {company_name}."),
                    "method": "tavily_llm_live",
                }
            except Exception:
                pass

        # Heuristic fallback
        risk_score = 35
        risk_flags = []
        for f in findings:
            fl = f.lower()
            if any(w in fl for w in ["disqualified", "struck off", "winding up", "wilful"]):
                risk_score += 20
                risk_flags.append("Adverse MCA finding detected")
            if "open charge" in fl or "charge created" in fl:
                risk_score += 10
        risk_score = min(risk_score, 100)

        return {
            "company_name": company_name,
            "cin": cin or "Not available",
            "web_findings": [f[:200] for f in findings[:3]],
            "risk_score": risk_score,
            "risk_flags": risk_flags,
            "compliance": {"compliance_score": max(0, 100 - risk_score)},
            "summary": f"Found {len(findings)} web results for MCA data on {company_name}. Manual verification recommended.",
            "method": "tavily_live",
            "note": "Full MCA data requires direct MCA21 portal access.",
        }

    except Exception as e:
        result = _get_demo_mca(company_name, cin)
        result["method"] = "mca_fallback"
        result["error"] = str(e)
        return result
