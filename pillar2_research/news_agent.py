"""
News Agent for Intelli-Credit.
Searches for company-related news using Tavily API and performs sentiment analysis.
In demo mode, returns realistic sample news data.
"""
import json
from config import IS_DEMO, has_tavily_key, has_llm_key, TAVILY_API_KEY, SAMPLE_DATA_DIR, get_llm_client
from utils import load_json


def search_company_news(company_name: str, promoter_names: list[str] = None) -> dict:
    """
    Search for news about a company and its promoters.
    Returns news articles with sentiment analysis.
    """
    if has_tavily_key():
        return _search_live(company_name, promoter_names or [])

    # Try free Google News scrape regardless of demo mode
    articles = _scrape_google_news(company_name)
    if articles:
        import hashlib
        sent_score = sum(a.get("sentiment_score", 0) for a in articles) / max(len(articles), 1)
        risk_score = max(0, min(100, int(50 - sent_score * 50)))
        return {
            "articles": articles,
            "overall_sentiment": round(sent_score, 2),
            "sentiment_label": "positive" if sent_score > 0.2 else "negative" if sent_score < -0.2 else "neutral",
            "sources_checked": len(articles),
            "search_queries": [f"{company_name} news"],
            "risk_score": risk_score,
            "summary": f"Found {len(articles)} recent news articles for {company_name}.",
            "method": "google_news_scrape",
        }

    return _get_demo_news(company_name)


def _get_demo_news(company_name: str = "Bharat Steel Industries") -> dict:
    """Return sample news data (pure mock — no network calls)."""
    sample = load_json(SAMPLE_DATA_DIR / "sample_company.json")
    news = sample["news_data"]
    import urllib.parse, hashlib
    demo_names = [sample.get("company_name", ""), "Reliance Industries", "Bharat Steel Industries"]
    cname = company_name if company_name else sample["company_name"]

    articles = []
    for art in news["articles"]:
        new_art = art.copy()
        for dn in demo_names:
            if dn:
                new_art["title"] = new_art["title"].replace(dn, cname)
                if "content_snippet" in new_art:
                    new_art["content_snippet"] = new_art["content_snippet"].replace(dn, cname)
        headline_query = urllib.parse.quote(new_art["title"])
        new_art["source"] = f"https://www.google.com/search?q={headline_query}"
        articles.append(new_art)

    seed = int(hashlib.md5(cname.lower().encode()).hexdigest(), 16) % 1000
    sent_score = 0.1 + (seed % 60) / 100.0
    risk_score = 15 + (seed % 25)

    return {
        "articles": articles,
        "overall_sentiment": sent_score,
        "sentiment_label": "positive" if sent_score > 0.2 else "neutral",
        "sources_checked": 4,
        "search_queries": [f"{cname} fraud NPA default", f"{cname} news"],
        "risk_score": risk_score,
        "summary": f"Overall news sentiment for {cname} is positive based on recent reports. Sector outlook remains stable.",
        "method": "demo",
    }


def _scrape_google_news(cname: str) -> list[dict]:
    """Scrape Google News for live articles as a free fallback (multi-selector + RSS)."""
    import requests
    import urllib.parse
    from bs4 import BeautifulSoup

    pos_words = ["growth", "profit", "surges", "jumps", "wins", "record", "soars", "positive",
                 "expansion", "approval", "success", "launch", "partner", "fund", "rise", "gain",
                 "boost", "upgrade", "lead", "award", "invest", "order", "revenue"]
    neg_words = ["loss", "falls", "slumps", "plunges", "lawsuit", "negative", "investigation",
                 "fraud", "default", "warning", "penalty", "scam", "fir", "fake", "violation",
                 "backlash", "scandal", "controversy", "fail", "decline", "probe", "accuse",
                 "guilty", "breach", "debt", "crisis", "drop", "concern", "wilful", "npa"]

    articles = []

    def _classify(title: str):
        t = title.lower()
        score = sum(0.35 for w in pos_words if w in t) - sum(0.35 for w in neg_words if w in t)
        score = max(-1.0, min(1.0, score))
        label = "positive" if score > 0.15 else "negative" if score < -0.15 else "neutral"
        return label, round(score if score != 0 else 0.05, 2)

    # Attempt 1: Google News HTML search (multi-selector for robustness)
    try:
        query = urllib.parse.quote(f"{cname} news India")
        url = f"https://news.google.com/search?q={query}&hl=en-IN&gl=IN&ceid=IN%3Aen"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(url, headers=headers, timeout=6)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            links = (soup.select("a.JtKRv")
                     or soup.select("article a[href*='articles']")
                     or soup.select("h3 a, h4 a"))
            for link in links[:7]:
                title = link.get_text(strip=True)
                if not title or len(title) < 10:
                    continue
                href = link.get("href", "")
                if href.startswith("."):
                    href = "https://news.google.com" + href[1:]
                label, score = _classify(title)
                articles.append({
                    "title": title,
                    "sentiment": label,
                    "sentiment_score": score,
                    "source": href,
                    "content_snippet": f"{label.capitalize()} news about {cname}.",
                })
    except Exception:
        pass

    # Attempt 2: Google News RSS fallback
    if not articles:
        try:
            query = urllib.parse.quote(cname)
            rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
            res = requests.get(rss_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=6)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "xml")
                for item in soup.find_all("item")[:7]:
                    title_tag = item.find("title")
                    link_tag = item.find("link")
                    if not title_tag:
                        continue
                    title_text = title_tag.get_text(strip=True)
                    label, score = _classify(title_text)
                    articles.append({
                        "title": title_text,
                        "sentiment": label,
                        "sentiment_score": score,
                        "source": link_tag.get_text(strip=True) if link_tag else "",
                        "content_snippet": f"{label.capitalize()} news signal from Google News RSS.",
                    })
        except Exception:
            pass

    return articles


def _search_live(company_name: str, promoter_names: list[str]) -> dict:
    """Search for live news using Tavily API."""
    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=TAVILY_API_KEY)

        # Build search queries
        queries = [
            f"{company_name} financial fraud default NPA",
            f"{company_name} recent expansion projects news",
            f"{company_name} regulatory penalties SEBI ROC",
        ]
        for name in promoter_names[:2]:
            queries.append(f"{name} {company_name} litigation background")

        all_articles = []
        for query in queries:
            try:
                result = client.search(query=query, max_results=3, search_depth="basic")
                for r in result.get("results", []):
                    all_articles.append({
                        "title": r.get("title", ""),
                        "source": r.get("url", ""),
                        "date": "",
                        "content_snippet": r.get("content", "")[:300],
                        "score": r.get("score", 0),
                    })
            except Exception:
                continue

        # Perform sentiment analysis using LLM if available
        sentiments = _analyze_sentiment(all_articles)

        overall = sum(a.get("sentiment_score", 0) for a in sentiments) / max(len(sentiments), 1)

        return {
            "articles": sentiments,
            "overall_sentiment": round(overall, 2),
            "sentiment_label": "positive" if overall > 0.2 else "negative" if overall < -0.2 else "neutral",
            "sources_checked": len(all_articles),
            "search_queries": queries,
            "risk_score": max(0, min(100, int(50 - overall * 50))),
            "summary": f"Found {len(all_articles)} articles. Overall sentiment: {'positive' if overall > 0 else 'negative' if overall < 0 else 'neutral'}.",
            "method": "tavily_live",
        }

    except Exception as e:
        result = _get_demo_news(company_name)
        result["method"] = "tavily_fallback"
        result["error"] = str(e)
        return result


def _analyze_sentiment(articles: list[dict]) -> list[dict]:
    """Analyze sentiment of articles using the configured LLM."""
    if not has_llm_key():
        return _keyword_sentiment(articles)

    try:
        llm = get_llm_client()
        if not llm:
            return _keyword_sentiment(articles)

        titles = [a.get("title", "") for a in articles]
        prompt = f"""Analyze the sentiment of these news headlines for credit risk assessment.
Focus on: fraud, defaults, litigation, NPA, promoter arrest = very negative; growth, orders, capacity expansion = positive.

Headlines:
{json.dumps(titles, indent=2)}

Return JSON array: [{{"title": "...", "sentiment": "positive/negative/neutral", "score": float (-1.0 to 1.0)}}]"""

        import asyncio
        response = llm.invoke(prompt)  # Using sync invoke for simplicity in this script
        content = response.content
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        sentiments = json.loads(content.strip())
        for i, article in enumerate(articles):
            if i < len(sentiments):
                article["sentiment"] = sentiments[i].get("sentiment", "neutral")
                article["sentiment_score"] = sentiments[i].get("score", 0)
        return articles
    except Exception:
        return _keyword_sentiment(articles)


def _keyword_sentiment(articles: list[dict]) -> list[dict]:
    """Simple keyword-based sentiment analysis fallback."""
    negative_words = {"fraud", "default", "npa", "litigation", "arrest", "scam", "wilful", "ban", "penalty", "fine", "dead", "death", "suicide", "murder", "killed", "police", "fir", "fake", "violation", "mock", "row ", "backlash", "misinformation", "expose", "scandal", "controversy", "critic", "fail", "delay", "decline", "trouble", "probe", "accuse", "guilty", "breach", "debt", "crisis", "drop", "concern", "worry", "plunge", "loss"}
    positive_words = {"growth", "expansion", "profit", "award", "order", "partnership", "investment", "launch", "partner", "empower", "excellence", "top", "innovat", "sustain", "compete", "win ", "hire", "placement", "recruit", "offer", "fund", "rise", "gain", "boost", "upgrade", "lead", "best", "excellent", "surpass"}

    for article in articles:
        title_lower = article.get("title", "").lower()
        neg_count = sum(1 for w in negative_words if w in title_lower)
        pos_count = sum(1 for w in positive_words if w in title_lower)

        if neg_count > pos_count:
            article["sentiment"] = "negative"
            article["sentiment_score"] = -0.3 * neg_count
        elif pos_count > neg_count:
            article["sentiment"] = "positive"
            article["sentiment_score"] = 0.3 * pos_count
        else:
            article["sentiment"] = "neutral"
            article["sentiment_score"] = 0.0

    return articles
