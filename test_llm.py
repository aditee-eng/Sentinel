import asyncio
from app.services.llm_reporter import generate_report

async def main():
    fake_diffs = [
        "v16.3.0-canary.67 - v16.3.0-canary.67",
        "v16.3.0-canary.66 - v16.3.0-canary.66",
        "v16.3.0-canary.65 - v16.3.0-canary.65",
        "v16.3.0-preview.5 - v16.3.0-preview.5",
    ]
    
    report = await generate_report("nextjs", fake_diffs)
    print("\n--- LLM GENERATED REPORT ---")
    print(report)

if __name__ == "__main__":
    asyncio.run(main())