import asyncio
from app.services.news_fetcher import get_news_mentions

async def main():
    results = await get_news_mentions("vercel")
    print(f"\nFound {len(results)} articles:\n")
    for r in results:
        print(f" - {r}")

if __name__ == "__main__":
    asyncio.run(main())