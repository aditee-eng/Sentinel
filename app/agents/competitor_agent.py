import os
import httpx
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from app.services.llm_reporter import generate_report

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# ---- Map competitor name to their GitHub repo ----
# Add more as you go. Leave blank string if no public repo.
COMPETITOR_REPOS = {
    "nextjs": "vercel/next.js",
    "supabase": "supabase/supabase",
    "zepto": "",       # no public repo - will skip
    "swiggy": "",      # no public repo - will skip
}


# ---- State definition ----
class CompetitorState(TypedDict):
    competitor: str
    current_findings: list
    previous_findings: list
    diffs: list
    report: str


# ---- Real GitHub fetcher ----
async def get_github_releases(repo: str) -> list:
    if not repo:
        return []
    
    url = f"https://api.github.com/repos/{repo}/releases"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"GitHub API error for {repo}: {response.status_code}")
        return []
    
    releases = response.json()
    return [
        f"{r['tag_name']} - {r['name'] or 'no title'}"
        for r in releases[:10]
    ]


# ---- Node 1: Searcher (now using REAL GitHub data) ----
async def searcher(state: CompetitorState):
    competitor = state["competitor"]
    repo = COMPETITOR_REPOS.get(competitor, "")
    
    current = await get_github_releases(repo)
    
    print(f"[{competitor}] Searcher found: {current}")
    
    return {
        **state,
        "current_findings": current
    }


# ---- Node 2: Diff (same as before, unchanged logic) ----
def diff_node(state: CompetitorState):
    current = set(state["current_findings"])
    previous = set(state.get("previous_findings", []))
    
    new_things = list(current - previous)
    
    print(f"[{state['competitor']}] New since last run: {new_things}")
    
    return {
        **state,
        "diffs": new_things,
        "previous_findings": state["current_findings"]
    }



# ---- Node 3: Reporter (now using real LLM) ----
async def reporter(state: CompetitorState):
    diffs = state["diffs"]
    competitor = state["competitor"]
    
    report = await generate_report(competitor, diffs)
    
    print(f"[{competitor}] Report: {report}")
    
    return {
        **state,
        "report": report
    }


# ---- Build the graph ----
def build_competitor_graph():
    graph = StateGraph(CompetitorState)
    
    graph.add_node("searcher", searcher)
    graph.add_node("diff_node", diff_node)
    graph.add_node("reporter", reporter)
    
    graph.set_entry_point("searcher")
    graph.add_edge("searcher", "diff_node")
    graph.add_edge("diff_node", "reporter")
    graph.add_edge("reporter", END)
    
    return graph