import os
import httpx
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

async def get_news_mentions(competitor: str, limit: int = 10) -> list:
    """
    Fetches recent news articles mentioning the competitor.
    Uses NewsAPI - covers 150,000+ sources worldwide.
    """
    url = "https://newsapi.org/v2/everything"
    
    params = {
    "q": f'"{competitor}"',  # exact phrase match with quotes
    "sortBy": "publishedAt",
    "pageSize": limit,
    "language": "en",
    "searchIn": "title,description",
    "apiKey": NEWS_API_KEY,  # trusted sources only
   }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
    
    if response.status_code != 200:
        print(f"NewsAPI error for {competitor}: {response.status_code}")
        return []
    
    articles = response.json().get("articles", [])
    
    filtered = [
        a for a in articles
        if a["title"] != "[Removed]"
        and competitor.lower() in (a["title"] or "").lower()  # must be in title
    ]
    
    return [
        f"[news] {a['title']} — {a['source']['name']} ({a['publishedAt'][:10]})"
        for a in articles
        if a["title"] != "[Removed]"  # filter deleted articles
    ]