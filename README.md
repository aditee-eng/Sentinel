# Sentinel

**An autonomous, multi-source competitive intelligence agent that tells you what your competitors shipped — before your PM asks.**

Sentinel watches a set of competitors across GitHub releases, community discussions, news, and pricing pages. It remembers what it saw last time, figures out exactly what changed, and writes a short, human-readable digest — automatically, on a schedule, with no manual checking required.

---

## The problem

Founders, PMs, and engineers waste hours every week manually checking what competitors are shipping — scrolling GitHub release pages, searching Reddit, refreshing pricing pages, reading tech news. It's repetitive, easy to miss things, and doesn't scale past 2-3 competitors.

Sentinel automates this end-to-end: give it a list of competitors, and it tells you exactly what's new, with sources and confidence levels, every time you check.

---
## Dashboard

![Sentinel Dashboard](dashboard.png)

> Windows 95-inspired UI — because good intelligence tools should be fast and functional, not pretty for the sake of it.

## Why this isn't "just an LLM wrapper"

Most AI agent projects are a single prompt wrapped in a nice UI. Sentinel is architected as a genuine **multi-agent system** with persistent memory:

- **Stateful across runs** — Sentinel remembers what it found last week and diffs against it. This isn't done by hand — it's powered by [LangGraph](https://www.langchain.com/langgraph)'s checkpointing system, backed by PostgreSQL.
- **Parallel agent execution** — each competitor is tracked by an independent sub-agent running concurrently, not in a sequential loop, using LangGraph's `Send` API.
- **Multi-source, not single-source** — findings are cross-referenced across GitHub, Reddit, news, and pricing pages rather than trusting one source blindly.
- **Confidence-aware reporting** — not all sources are equally trustworthy (a Reddit rumor isn't the same as a verified pricing page change). Sentinel is designed to weight and validate signals rather than report everything at face value.

---

## Architecture

```
                         ┌─────────────┐
                         │  Orchestrator│
                         │  (Planner)   │
                         └──────┬──────┘
                                │ spawns parallel agents (Send API)
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
      ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
      │ Competitor A  │ │ Competitor B  │ │ Competitor C  │
      │   Agent       │ │   Agent       │ │   Agent       │
      ├───────────────┤ ├───────────────┤ ├───────────────┤
      │ 1. Search     │ │ 1. Search     │ │ 1. Search     │
      │ 2. Diff vs    │ │ 2. Diff vs    │ │ 2. Diff vs    │
      │    last run   │ │    last run   │ │    last run   │
      │ 3. LLM report │ │ 3. LLM report │ │ 3. LLM report │
      └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
              │                 │                 │
              └─────────────────┼─────────────────┘
                                ▼
                         ┌─────────────┐
                         │  Aggregator │
                         └──────┬──────┘
                                ▼
                    PostgreSQL (state + history)
                                │
                                ▼
                      FastAPI → React Dashboard
```

Each competitor agent's state (what it found, what changed, the generated report) is checkpointed to PostgreSQL after every step. This means:
- The system survives crashes mid-run without losing progress
- Every historical run is queryable — you can see how a competitor's trajectory looked 6 weeks ago
- Each competitor's memory is fully isolated from the others (via separate `thread_id`s)

---

## Tech stack

| Layer | Technology |
|---|---|
| Agent orchestration | LangGraph (state graphs, parallel `Send` API, checkpointing) |
| LLM | Llama 3.3 70B via Groq |
| Backend | FastAPI (Python, async) |
| Database | PostgreSQL (Neon) — both app data and LangGraph checkpoint storage |
| Data sources | GitHub REST API, Reddit JSON API, NewsAPI, Playwright (pricing page scraping) |
| Frontend | React |

---

## How it works

1. **You define competitors** — give Sentinel a list of companies to track, optionally mapping each to a GitHub repo, subreddit, or pricing page URL.
2. **The orchestrator plans the run** — decides which competitors to check and spawns one independent agent per competitor, all running in parallel.
3. **Each agent searches its sources** — fetches GitHub releases, Reddit mentions, news articles, and pricing page snapshots concurrently.
4. **State is loaded and diffed** — LangGraph's checkpointer automatically loads each competitor's previous findings from PostgreSQL, and the agent computes exactly what's new since the last run.
5. **An LLM writes the digest** — Llama 3.3 70B (via Groq) turns the raw diff into a short, readable summary — not a dump of raw data.
6. **Everything is persisted** — every run's full state is saved, so historical trends are queryable later.

---

## Project status

This project is being built incrementally and documented honestly as it progresses.

- [x] LangGraph state graph for a single competitor agent (search → diff → report)
- [x] PostgreSQL-backed checkpointing for persistent cross-run memory
- [x] Real GitHub releases as a working data source
- [x] LLM-generated natural language reports (Llama 3.3 70B via Groq)
- [ ] Additional data sources: Reddit, NewsAPI, Playwright-based pricing page diffing
- [ ] Multi-competitor parallel orchestration (`Send` API)
- [ ] Source confidence scoring / cross-source validation
- [ ] FastAPI endpoints serving dashboard data
- [ ] React dashboard with historical trend view

---

## Local setup

```bash
# clone and enter the repo
git clone https://github.com/yourusername/sentinel.git
cd sentinel

# set up virtual environment
python3 -m venv venv
source venv/bin/activate

# install dependencies
pip install -r requirements.txt
playwright install chromium

# add your environment variables
cp .env.example .env
# then fill in DATABASE_URL, GROQ_API_KEY, GITHUB_TOKEN
```

You'll need:
- A free [Neon](https://neon.tech) or [Supabase](https://supabase.com) PostgreSQL instance
- A free [Groq](https://console.groq.com) API key
- A [GitHub personal access token](https://github.com/settings/tokens) (no special scopes needed for public repo reads)

---

## Why I built this

Most browser/research AI agents try to do everything by clicking through UIs the way a human would — which is slow and unreliable, since LLMs are much better at reasoning over structured data than navigating messy web pages. Sentinel takes the opposite approach for a real, recurring problem: pull structured signal directly from APIs and targeted scraping, keep persistent memory of what's already been seen, and let the LLM focus on what it's actually good at — synthesizing a clear report from a clean diff, not parsing raw HTML.