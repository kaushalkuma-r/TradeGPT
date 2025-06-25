"""
LLM-based intent detector.
Returns:
    intent -> one of {"VIEW_WITH_STRATEGY", "VIEW_NO_STRATEGY", "OTHER"}
"""
import json, requests
from utils.config import OPENROUTER_API_KEY, OPENROUTER_MODEL

_API = "https://openrouter.ai/api/v1/chat/completions"

_SYSTEM = (
    "You are an intent classifier for a trading chatbot. "
    "Return exactly one label from this set:\n"
    "VIEW_WITH_STRATEGY   - user shares a market/sector view AND explicitly wants trade ideas / strategies\n"
    "VIEW_NO_STRATEGY     - user shares a market/sector view but does NOT ask for strategies (might just discuss)\n"
    "OTHER                - any other chit-chat, greeting, question, etc.\n\n"
    "Output ONLY the label."
)

def detect_intent(user_msg: str) -> str:
    try:
        resp = requests.post(
            _API,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user",   "content": user_msg}
                ]
            })
        )
        resp.raise_for_status()
        label = resp.json()["choices"][0]["message"]["content"].strip().upper()
        if label not in {"VIEW_WITH_STRATEGY", "VIEW_NO_STRATEGY", "OTHER"}:
            label = "OTHER"          # fallback
        return label
    except Exception:
        return "OTHER" 