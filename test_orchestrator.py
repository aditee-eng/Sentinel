import asyncio
from app.agents.orchestrator import build_orchestrator


async def main():
    graph = build_orchestrator()
    app = graph.compile()

    result = await app.ainvoke({
    "competitors": ["razorpay", "cashfree", "payu"],
    "all_reports": []
    })
    print("\n===== FINAL REPORTS =====")
    
    seen = set()
    for r in result["all_reports"]:
        if r["competitor"] not in seen:
            seen.add(r["competitor"])
            print(f"\n[{r['competitor'].upper()}]")
            print(r["report"])

if __name__ == "__main__":
    asyncio.run(main())