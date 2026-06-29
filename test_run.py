import asyncio
from app.db.connection import get_checkpointer
from app.agents.competitor_agent import build_competitor_graph

async def run_once():
    graph = build_competitor_graph()

    async with get_checkpointer() as checkpointer:
        app = graph.compile(checkpointer=checkpointer)

        config = {"configurable": {"thread_id": "rival-nextjs"}}

        existing_state = await app.aget_state(config)

        if existing_state.values:
            print(">>> Found previous state, continuing...")
            input_data = {"competitor": "nextjs"}
        else:
            print(">>> No previous state, starting fresh...")
            input_data = {
                "competitor": "nextjs",
                "current_findings": [],
                "previous_findings": [],
                "diffs": [],
                "report": ""
            }

        result = await app.ainvoke(input_data, config=config)

        print("\n--- FINAL STATE ---")
        print(result)


if __name__ == "__main__":
    asyncio.run(run_once())