from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# from utils.config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from utils.memory import memory
from utils.charts import generate_plotly_charts
from utils.parsing import extract_sector_summary, parse_strategies, build_response_summary
from utils.llm_client import call_openrouter

app = FastAPI()

class ChatMessage(BaseModel):
    message: str

@app.post("/chat")
async def chat(chat_message: ChatMessage):
    context = memory.load_memory_variables({})
    combined_prompt = f"{context['history']}\nUser: {chat_message.message}"

    prompt = f"""
You are a highly knowledgeable trading assistant. A user has a market view or belief as follows:
"{chat_message.message}"

Your response should be structured in two sections:

---

**1. Sector & View Summary:**  
Provide two paragraphs summarizing:
- The relevant sector(s) the user's view pertains to (e.g., telecom, tech, energy).
- The user's directional view (bullish/bearish/neutral) and reasoning based on the input.

---

**2. Trading Strategies:**  
Recommend at least **three unique, well-justified short- to medium-term trading strategies** aligned with the user's view.  
Each strategy should be:
- Distinct and non-overlapping
- Commonly used in real-world trading
- Actionable (not long-term investing)

**For each strategy, use the exact structure:**

- Strategy: [Name of the strategy]
- Explanation: [What it is, how it works, how it connects to the user's view. Include instruments and reasoning.]
- Popularity: [X]%
- Average Return: [Y]%
- Sharpe Ratio: [Z]
- Win Rate: [W]%
- Max Drawdown: [D]%
- Profit Factor: [P]
- Volatility: [V]%
- Expectancy: [E]% per trade
- Trade Frequency: [T] trades/month

---

⚠️ Important:
- Do NOT include fewer than 3 strategies.
- Each strategy block must begin with 'Strategy:' and end with '---'.
- Use exact format for each metric. No markdown, bold, or extra commentary.
- You are being evaluated on strict format adherence.

Only return the 3+ structured strategy blocks. Avoid summaries, disclaimers, or repetition.
"""
    try:
        raw_text = call_openrouter(prompt)
        sector_summary = extract_sector_summary(raw_text)
        strategies = parse_strategies(raw_text)
        response_summary = build_response_summary(strategies)
        memory.save_context({"input": chat_message.message}, {"output": response_summary})
        charts = generate_plotly_charts(strategies)
        return {
            "response": response_summary.strip(),
            "strategies": strategies,
            "charts": {k: fig.to_dict() for k, fig in charts.items()},
            "sector_view_summary": sector_summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to the Trading Chatbot Backend (OpenRouter Modularized)"}
