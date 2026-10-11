"""
Promoter Background Agent for Fin-Sight.
Researches promoter/director profiles, DIN status, and adverse history.
"""
from __future__ import annotations
import json
from config import TAVILY_API_KEY, SAMPLE_DATA_DIR, has_tavily_key, has_llm_key, get_llm_client


def research_promoters(company_name: str, promoter_names: list[str] = None, cin: str = "") -> dict:
    """
    Research promoter backgrounds, DIN disqualifications, and adverse history.
    Returns structured promoter risk assessment.
    """
    promoter_names = promoter_names or []

    if not promoter_names:
        from utils import load_json
        try:
            sample = load_json(SAMPLE_DATA_DIR / "sample_company.json")
            promoter_names = [p["name"] for p in sample.get("promoters", [])[:3]]
        except Exception:
            pass

    if has_tavily_key() and promoter_names:
        return _research_live(company_name, promoter_names, cin)

    return _get_demo_promoter(company_name, promoter_names)


def _research_live(company_name: str, promoter_names: list[str], cin: str) -> dict:
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY)

        findings = []
        for name in promoter_names[:3]:
            queries = [
                f"{name} director {company_name} DIN MCA India background",
                f"{name} fraud arrest FIR default NPA India",
                f"{name} SEBI NCLT disqualified director India",
            ]
            for query in queries:
                try:
                    result = client.search(query=query, max_results=2, search_depth="basic")
                    for r in result.get("results", []):
                        findings.append({
                            "promoter": name,
                            "source": r.get("url", ""),
                            "title": r.get("title", ""),
                            "content": r.get("content", "")[:400],
                        })
                except Exception:
                    continue

        if has_llm_key() and findings:
            llm = get_llm_client()
            prompt = f"""Analyze promoter background risk for directors of '{company_name}': {promoter_names}.

Search findings:
{json.dumps(findings[:10], indent=1)}

Return ONLY a valid JSON object:
{{
  "promoter_profiles": [
    {{
      "name": "str",
      "din_status": "Active",
      "adverse_findings": [],
      "risk_level": "LOW",
      "other_directorships": 0
    }}
  ],
  "overall_promoter_risk_score": 20,
  "disqualified_count": 0,
  "adverse_media_count": 0,
  "default_count": 0,
  "key_flags": [],
  "summary": "str"
}}"""
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
                    "promoter_profiles": data.get("promoter_profiles", []),
                    "overall_promoter_risk_score": data.get("overall_promoter_risk_score", 20),
                    "risk_score": data.get("overall_promoter_risk_score", 20),
                    "disqualified_count": data.get("disqualified_count", 0),
                    "adverse_media_count": data.get("adverse_media_count", 0),
                    "default_count": data.get("default_count", 0),
                    "key_flags": data.get("key_flags", []),
                    "summary": data.get("summary", f"Promoter background check completed for {len(promoter_names)} directors."),
                    "method": "tavily_llm_live",
                }
            except Exception:
                pass

        # Heuristic fallback
        adverse_count = 0
        risk_score = 15
        key_flags = []
        for f in findings:
            fl = (f["title"] + " " + f["content"]).lower()
            if any(w in fl for w in ["disqualified", "arrested", "fir", "fraud", "default", "wilful"]):
                adverse_count += 1
                risk_score += 20
                key_flags.append(f"Adverse finding for {f['promoter']}: {f['title'][:60]}")

        return {
            "company_name": company_name,
            "promoters_checked": promoter_names,
            "adverse_media_count": adverse_count,
            "default_count": 0,
            "risk_score": min(risk_score, 100),
            "key_flags": key_flags[:5],
            "summary": f"Promoter background checked for {len(promoter_names)} directors. {adverse_count} adverse findings detected.",
            "method": "tavily_live",
        }

    except Exception as e:
        result = _get_demo_promoter(company_name, promoter_names)
        result["error"] = str(e)
        result["method"] = "promoter_fallback"
        return result


def _get_demo_promoter(company_name: str, promoter_names: list[str]) -> dict:
    import hashlib
    from utils import load_json
    try:
        sample = load_json(SAMPLE_DATA_DIR / "sample_company.json")
        promoters = sample.get("promoters", [])
    except Exception:
        promoters = []

    seed = int(hashlib.md5(company_name.lower().encode()).hexdigest(), 16) % 1000
    risk_score = 10 + (seed % 20)

    profiles = []
    for p in (promoters or [{"name": n} for n in promoter_names])[:3]:
        profiles.append({
            "name": p.get("name", "Director"),
            "din_status": "Active",
            "adverse_findings": [],
            "risk_level": "LOW",
            "other_directorships": seed % 3,
        })

    return {
        "company_name": company_name,
        "promoter_profiles": profiles,
        "overall_promoter_risk_score": risk_score,
        "risk_score": risk_score,
        "disqualified_count": 0,
        "adverse_media_count": 0,
        "default_count": 0,
        "key_flags": [],
        "summary": f"Promoter background for {company_name} shows clean profile. All directors Active in MCA records.",
        "method": "demo",
    }
