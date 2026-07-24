from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.agents.orchestrator import build_orchestrator
from app.db.connection import get_checkpointer
from app.agents.competitor_agent import build_competitor_graph

router = APIRouter(prefix="/api")

# Default competitor set — used if the caller doesn't specify one.
# /api/competitors below reflects whatever was last run, not this default,
# once at least one run has happened.
DEFAULT_COMPETITORS = ["razorpay", "cashfree", "payu"]

# Tracks the most recently used competitor list in memory, so
# /api/competitors and /api/stats stay in sync with what /api/run used.
# NOTE: this is in-memory only — resets on server restart. For real
# multi-user persistence, this should move to the DB.
_last_competitors = DEFAULT_COMPETITORS


class RunRequest(BaseModel):
    competitors: Optional[list[str]] = None


@router.post("/run")
async def run_sentinel(payload: RunRequest = RunRequest()):
    """
    Triggers a full Sentinel run.
    Pass {"competitors": ["stripe", "razorpay"]} in the request body
    to track a custom set; omit it to use the default set.
    """
    global _last_competitors
    competitors = payload.competitors if payload.competitors else DEFAULT_COMPETITORS
    _last_competitors = competitors

    graph = build_orchestrator()
    app = graph.compile()

    result = await app.ainvoke({
        "competitors": competitors,
        "all_reports": []
    })

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
    Returns the competitor list from the most recent run
    (or the default set if nothing has run yet).
    """
    return {"competitors": _last_competitors}


@router.get("/reports/{competitor}")
async def get_latest_report(competitor: str):
    graph = build_competitor_graph()

    async with get_checkpointer() as checkpointer:
        app = graph.compile(checkpointer=checkpointer)

        config = {"configurable": {"thread_id": f"sentinel-{competitor}"}}
        state = await app.aget_state(config)

        if not state.values:
            return {"competitor": competitor, "report": "No data yet — run Sentinel first."}

        return {
            "competitor": competitor,
            "report": state.values.get("report", "No report generated yet."),
            "last_findings_count": len(state.values.get("current_findings", []))
        }


@router.get("/stats")
async def get_stats():
    """
    Returns cross-competitor stats for dashboard visualizations,
    based on the most recently run competitor list.
    """
    graph = build_competitor_graph()
    stats = []

    async with get_checkpointer() as checkpointer:
        app = graph.compile(checkpointer=checkpointer)

        for competitor in _last_competitors:
            config = {"configurable": {"thread_id": f"sentinel-{competitor}"}}
            state = await app.aget_state(config)

            if not state.values:
                stats.append({
                    "competitor": competitor,
                    "total_findings": 0,
                    "news_count": 0,
                    "pricing_count": 0,
                    "github_count": 0,
                    "new_this_run": 0
                })
                continue

            findings = state.values.get("current_findings", [])
            diffs = state.values.get("diffs", [])

            news = [f for f in findings if f.startswith("[news]")]
            pricing = [f for f in findings if f.startswith("[pricing]")]
            github = [f for f in findings if not f.startswith("[news]") and not f.startswith("[pricing]")]

            stats.append({
                "competitor": competitor,
                "total_findings": len(findings),
                "news_count": len(news),
                "pricing_count": len(pricing),
                "github_count": len(github),
                "new_this_run": len(diffs)
            })

    return {"stats": stats}