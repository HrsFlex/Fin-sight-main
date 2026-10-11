"""
Bank Statement Agent for Fin-Sight.
Analyzes uploaded bank statement text for behavioral banking signals:
bounces, TOD usage, circular transactions, OD utilization, salary patterns.
"""
from __future__ import annotations
import json
import re
from config import SAMPLE_DATA_DIR, has_llm_key, get_llm_client


def analyze_bank_statement(full_text: str, company_name: str = "") -> dict:
    """
    Analyze bank statement text for credit behavioral signals.
    Returns structured banking risk profile.
    """
    if not full_text or len(full_text) < 50:
        return _get_demo_banking(company_name)

    if has_llm_key():
        result = _analyze_with_llm(full_text, company_name)
        if result:
            return result

    return _analyze_heuristic(full_text, company_name)


def _analyze_with_llm(text: str, company_name: str) -> dict | None:
    try:
        llm = get_llm_client()
        # Truncate to avoid token overflow
        excerpt = text[:4000]
        prompt = f"""Analyze this bank statement for '{company_name}' and extract key credit risk indicators.

Bank statement excerpt:
{excerpt}

Return ONLY a valid JSON object:
{{
  "bank_name": "str",
  "account_type": "Current/Savings/OD",
  "average_daily_balance_cr": 0.0,
  "od_limit_cr": 0.0,
  "utilization_pct": 0.0,
  "bounce_count": 0,
  "tod_instances": 0,
  "emi_debits_count": 0,
  "salary_credits": 0,
  "circular_transaction_flag": false,
  "banking_risk_score": 20,
  "risk_level": "LOW",
  "key_observations": [],
  "summary": "str"
}}
Guidelines:
- bounce_count: returned/bounced cheques or ECS returns
- tod_instances: temporary overdraft or limit breach events
- circular_transaction_flag: same-day round-trip credits/debits suggesting circular transactions
- utilization_pct: OD/CC limit utilization percentage (0-100)
- banking_risk_score: 0 (very low risk) to 100 (very high risk)
If a field cannot be determined, use sensible defaults."""
        response = llm.invoke(prompt)
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        data = json.loads(content.strip())
        return {
            "company_name": company_name,
            "bank_name": data.get("bank_name", "Unknown Bank"),
            "account_type": data.get("account_type", "Current"),
            "average_daily_balance_cr": data.get("average_daily_balance_cr", 0.0),
            "od_limit_cr": data.get("od_limit_cr", 0.0),
            "utilization_pct": data.get("utilization_pct", 0.0),
            "bounce_count": data.get("bounce_count", 0),
            "tod_instances": data.get("tod_instances", 0),
            "emi_debits_count": data.get("emi_debits_count", 0),
            "salary_credits": data.get("salary_credits", 0),
            "circular_transaction_flag": data.get("circular_transaction_flag", False),
            "banking_risk_score": data.get("banking_risk_score", 20),
            "risk_level": data.get("risk_level", "LOW"),
            "key_observations": data.get("key_observations", []),
            "summary": data.get("summary", f"Bank statement analysis completed for {company_name}."),
            "method": "llm_extraction",
        }
    except Exception:
        return None


def _analyze_heuristic(text: str, company_name: str) -> dict:
    """Regex-based heuristic extraction from bank statement text."""
    tl = text.lower()

    # Bounce / returns
    bounce_patterns = [
        r"(?:cheque\s+)?return(?:ed)?",
        r"ecs\s+return",
        r"nach\s+return",
        r"inward\s+return",
        r"outward\s+return",
        r"dishonour",
    ]
    bounce_count = sum(len(re.findall(p, tl)) for p in bounce_patterns)

    # TOD (temporary overdraft)
    tod_count = len(re.findall(r"(?:tod|temporary\s+overdraft|excess\s+withdrawal|od\s+utilized)", tl))

    # EMI debits
    emi_count = len(re.findall(r"(?:emi|equated\s+monthly|loan\s+debit|ecs\s+debit)", tl))

    # Salary credits
    salary_count = len(re.findall(r"(?:salary|payroll|remuneration|wages)", tl))

    # Circular transactions — same-day large debits + credits
    circular_flag = bool(re.search(r"(?:transfer|neft|rtgs|imps).{0,50}(?:transfer|neft|rtgs|imps)", tl))

    # Bank name
    bank_match = re.search(
        r"(?:state\s+bank|sbi|hdfc|icici|axis|kotak|pnb|canara|union\s+bank|bank\s+of\s+baroda|idbi|yes\s+bank|indusind)",
        tl,
    )
    bank_name = bank_match.group(0).title().replace("Sbi", "SBI") if bank_match else "Unknown Bank"

    # OD limit
    od_match = re.search(r"(?:od|cc|cash\s+credit)\s+limit[:\s]+(?:rs\.?\s*)?(\d[\d,\.]+)", tl)
    od_limit = float(od_match.group(1).replace(",", "")) / 1e7 if od_match else 0.0

    # Average balance
    bal_match = re.search(r"average\s+(?:daily\s+)?balance[:\s]+(?:rs\.?\s*)?(\d[\d,\.]+)", tl)
    avg_balance = float(bal_match.group(1).replace(",", "")) / 1e7 if bal_match else 0.0

    # Risk scoring
    risk_score = 15
    if bounce_count >= 3:
        risk_score += 30
    elif bounce_count >= 1:
        risk_score += 15
    if tod_count >= 2:
        risk_score += 20
    elif tod_count >= 1:
        risk_score += 10
    if circular_flag:
        risk_score += 15
    risk_score = min(risk_score, 100)

    risk_level = "LOW" if risk_score < 30 else "MODERATE" if risk_score < 60 else "HIGH"

    obs = []
    if bounce_count > 0:
        obs.append(f"{bounce_count} cheque/ECS return(s) detected")
    if tod_count > 0:
        obs.append(f"{tod_count} TOD/overdraft breach(es) detected")
    if circular_flag:
        obs.append("Potential circular transaction pattern detected")

    return {
        "company_name": company_name,
        "bank_name": bank_name,
        "account_type": "Current",
        "average_daily_balance_cr": round(avg_balance, 2),
        "od_limit_cr": round(od_limit, 2),
        "utilization_pct": 0.0,
        "bounce_count": bounce_count,
        "tod_instances": tod_count,
        "emi_debits_count": emi_count,
        "salary_credits": salary_count,
        "circular_transaction_flag": circular_flag,
        "banking_risk_score": risk_score,
        "risk_level": risk_level,
        "key_observations": obs,
        "summary": f"Heuristic bank statement analysis: {bounce_count} bounces, {tod_count} TOD instances. Risk: {risk_level}.",
        "method": "heuristic",
    }


def _get_demo_banking(company_name: str) -> dict:
    import hashlib
    seed = int(hashlib.md5((company_name or "demo").lower().encode()).hexdigest(), 16) % 1000
    avg_bal = 2.5 + (seed % 50) / 10.0
    od_limit = 5.0 + (seed % 20) / 2.0
    utilization = 30 + seed % 40
    risk_score = 15 + seed % 20

    return {
        "company_name": company_name,
        "bank_name": "HDFC Bank",
        "account_type": "Current",
        "average_daily_balance_cr": round(avg_bal, 2),
        "od_limit_cr": round(od_limit, 2),
        "utilization_pct": utilization,
        "bounce_count": 0,
        "tod_instances": 0,
        "emi_debits_count": seed % 3,
        "salary_credits": 12,
        "circular_transaction_flag": False,
        "banking_risk_score": risk_score,
        "risk_level": "LOW",
        "key_observations": [f"Average daily balance: Rs. {avg_bal:.1f} Cr", f"OD utilization at {utilization}%"],
        "summary": f"Banking behavior for {company_name} shows stable patterns with no adverse signals. OD utilization within acceptable range.",
        "method": "demo",
    }
