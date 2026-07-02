from fastapi import APIRouter
from app.agents.orchestrator import build_orchestrator
from app.db.connection import get_checkpointer
from app.agents.competitor_agent import build_competitor_graph

router = APIRouter(prefix="/api")

# hardcoded for now — will make configurable later
COMPETITORS = ["razorpay", "cashfree", "payu"]


@router.post("/run")
async def run_sentinel():
    """
    Triggers a full Sentinel run for all competitors.
    Returns all reports once complete.
    """
    graph = build_orchestrator()
    app = graph.compile()

    result = await app.ainvoke({
        "competitors": COMPETITORS,
        "all_reports": []
    })

    # deduplicate reports
    seen = set()
    reports = []
    for r in result["all_reports"]:
        if r["competitor"] not in seen:
            seen.add(r["competitor"])
            reports.append(r)

    return {"reports": reports}


@router.get("/competitors")
async def get_competitors():
    """
    Returns the list of competitors being tracked.
    """
    return {"competitors": COMPETITORS}


@router.get("/reports/{competitor}")
async def get_latest_report(competitor: str):
    graph = build_competitor_graph()
    
    async with get_checkpointer() as checkpointer:
        app = graph.compile(checkpointer=checkpointer)
        
        # must match the thread_id used in orchestrator
        config = {"configurable": {"thread_id": f"sentinel-{competitor}"}}
        state = await app.aget_state(config)
        
        if not state.values:
            return {"competitor": competitor, "report": "No data yet — run Sentinel first."}
        
        return {
            "competitor": competitor,
            "report": state.values.get("report", "No report generated yet."),
            "last_findings_count": len(state.values.get("current_findings", []))
        }