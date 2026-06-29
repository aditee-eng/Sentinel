import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0.3  # low temperature - we want factual, not creative
)

async def generate_report(competitor: str, diffs: list) -> str:
    if not diffs:
        return f"No new updates from {competitor} this week."
    
    diffs_text = "\n".join(f"- {d}" for d in diffs)
    
    prompt = f"""You are a competitive intelligence analyst. 
Write a short, clear report (3-4 sentences max) summarizing what {competitor} has shipped or changed recently, based on this raw data:

{diffs_text}

Write it like a smart colleague giving a quick update - direct, no fluff, no corporate language. 
If there are many version releases, summarize the pattern (e.g. "rapid iteration on X area") rather than listing every single one."""

    response = await llm.ainvoke(prompt)
    return response.content