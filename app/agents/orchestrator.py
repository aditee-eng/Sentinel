import asyncio
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.types import Send
from app.agents.competitor_agent import CompetitorState, build_competitor_graph
from app.db.connection import get_checkpointer

from typing import TypedDict, Annotated
import operator

# ---- Orchestrator State ----
class OrchestratorState(TypedDict):
    # Annotated with operator.add means:
    # "when multiple agents write to all_reports, ADD their lists together"
    competitors: list                            # plain list, only planner writes this
    all_reports: Annotated[list, operator.add] 


# ---- Node 1: Planner ----
def planner(state: OrchestratorState):
    print(f"[Orchestrator] Planning run for: {state['competitors']}")
    return {
        **state,
        "all_reports": []
    }


# ---- Node 2: Spawn parallel agents ----
def spawn_agents(state: OrchestratorState):
    print(f"[Orchestrator] Spawning {len(state['competitors'])} parallel agents...")
    return [
        Send("competitor_agent", {
            "competitor": c,
            "current_findings": [],
            "previous_findings": [],
            "diffs": [],
            "report": ""
        })
        for c in state["competitors"]
    ]


# ---- Node 3: Aggregator ----
def aggregator(state: OrchestratorState):
    print(f"\n[Orchestrator] All agents done. Collecting reports...")
    return state


# ---- Per-competitor entry node ----
# This is the entry point for each spawned agent
# It immediately hands off to the full competitor graph logic
async def competitor_agent(state: CompetitorState):
    competitor = state["competitor"]
    graph = build_competitor_graph()

    async with get_checkpointer() as checkpointer:
        app = graph.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": f"sentinel-{competitor}"}}
        existing = await app.aget_state(config)

        if existing.values:
            input_data = {"competitor": competitor}
        else:
            input_data = {
                "competitor": competitor,
                "current_findings": [],
                "previous_findings": [],
                "diffs": [],
                "report": ""
            }

        result = await app.ainvoke(input_data, config=config)

    # only return all_reports — don't touch competitors at all
    return {
        "all_reports": [{"competitor": competitor, "report": result["report"]}]
    }


# ---- Build orchestrator graph ----
def build_orchestrator():
    graph = StateGraph(OrchestratorState)

    graph.add_node("planner", planner)
    graph.add_node("competitor_agent", competitor_agent)
    graph.add_node("aggregator", aggregator)

    graph.set_entry_point("planner")
    graph.add_conditional_edges(
        "planner",
        spawn_agents,
        ["competitor_agent"]
    )
    graph.add_edge("competitor_agent", "aggregator")
    graph.add_edge("aggregator", END)

    return graph