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
    Below is raw data about {competitor} from multiple sources. Some items may be noise or unrelated packages/projects that share the name — ignore those completely.

    Focus ONLY on meaningful signals about {competitor} the company/product:
   - New features or product launches
   - Pricing changes
   - Major news coverage
   - Significant community activity

   Raw data:
  {diffs_text}

   Write a 3-4 sentence report summarizing only the genuinely relevant updates. 
   If everything looks like noise with no real signal, say "No meaningful updates found for {competitor} this week."
   Write like a smart colleague giving a quick update — direct, no fluff."""

    response = await llm.ainvoke(prompt)
    return response.content