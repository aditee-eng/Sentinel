import asyncio
from app.services.playwright_fetcher import get_pricing_data

async def main():
    print("Fetching Vercel pricing...")
    results = await get_pricing_data("nextjs")
    print(f"\nFound {len(results)} pricing items:\n")
    for r in results:
        print(f" - {r}")

if __name__ == "__main__":
    asyncio.run(main())