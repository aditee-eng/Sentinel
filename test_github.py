import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

async def get_github_releases(repo: str) -> list:
    url = f"https://api.github.com/repos/{repo}/releases"
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"GitHub API error: {response.status_code} - {response.text}")
        return []
    
    releases = response.json()
    
    return [
        f"{r['tag_name']} - {r['name'] or 'no title'}"
        for r in releases[:10]
    ]


async def main():
    results = await get_github_releases("vercel/next.js")
    print(f"\nFound {len(results)} releases:")
    for r in results:
        print(f" - {r}")


if __name__ == "__main__":
    asyncio.run(main())