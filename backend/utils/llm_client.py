import requests
import json
import os
from dotenv import load_dotenv
from time import time
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY_INTENT")
OPENROUTER_MODEL = "deepseek/deepseek-chat-v3-0324:free" #

_API = "https://openrouter.ai/api/v1/chat/completions"

_SYSTEM = (
    "You are an intent classifier for a trading chatbot. "
    "Return exactly one label from this set:\n"
    "VIEW_WITH_STRATEGY   - user shares a market/sector view AND explicitly wants trade ideas / strategies\n"
    "VIEW_NO_STRATEGY     - user shares a market/sector view but does NOT ask for strategies (might just discuss)\n"
    "OTHER                - any other chit-chat, greeting, question, etc.\n\n"
    "Output ONLY the label."
)

def call_openrouter(prompt):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://your-site.com",
            "X-Title": "TradingStrategyBot"
        },
        data=json.dumps({
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        })
    )
    # time.sleep(2)
    response.raise_for_status()
    llm_response = response.json()
    return llm_response["choices"][0]["message"]["content"] 


def detect_intent(user_msg: str) -> str:
    try:
        # time.sleep(2)
        response = requests.post(
            url=_API,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://your-site.com",
                "X-Title": "TradingStrategyBot"
            },
            data=json.dumps({
                "model": OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user", "content": user_msg}
                ]
            })
        )
        response.raise_for_status()
        llm_response = response.json()
        label = llm_response["choices"][0]["message"]["content"].strip().upper()
        if label not in {"VIEW_WITH_STRATEGY", "VIEW_NO_STRATEGY", "OTHER"}:
            label = "OTHER"
        return label
    except Exception:
        return "OTHER"
