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
Below is raw data about {competitor} from multiple sources. Some items may be noise — ignore those.

Focus ONLY on meaningful signals about {competitor} the company/product:
- New features or product launches
- Pricing changes
- Major news coverage
- Business developments (IPO, funding, partnerships)

Raw data:
{diffs_text}

Write EXACTLY 3 bullet points max. Each bullet must be:
- One punchy line under 15 words
- Start with a dash (-)
- No emojis, no paragraphs, no fluff
- Each bullet on its own line

If everything is noise, respond with exactly:
- No meaningful updates this week.

Example format:
- Filed for $600M IPO via confidential route
- Partnered with BiteSpeed for AI-powered D2C stack
- SEBI seeks clarification on draft prospectus"""
    response = await llm.ainvoke(prompt)
    return response.content