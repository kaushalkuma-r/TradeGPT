def view_follow_up_prompt(user_msg: str) -> str:
    return (
        f"You are an engaging financial chatbot. The user said:\n"
        f"“{user_msg}”\n\n"
        "Respond conversationally, acknowledge their view, and ask if they'd like "
        "you to suggest specific trading strategies. Keep it short."
    )

def strategy_prompt(user_msg: str) -> str:
    return f"""
You are a highly knowledgeable trading assistant. A user has a market view or belief as follows:
"{user_msg}"

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