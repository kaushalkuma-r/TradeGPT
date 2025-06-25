from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from utils.memory  import memory
from utils.charts  import generate_plotly_charts
from utils.parsing import (
    extract_sector_summary,
    parse_strategies,
    build_response_summary,
)
from utils.llm_client   import call_openrouter,detect_intent      
from utils.prompts      import view_follow_up_prompt, strategy_prompt

app = FastAPI()

STATE_FLAG = "awaiting_strategy_confirmation"   # key in memory
LAST_VIEW  = "last_view"                        # key in memory

class ChatMessage(BaseModel):
    message: str

# ─────────────────────────────────────────────────────────────────────────
@app.post("/chat")
async def chat(chat_message: ChatMessage):
    user_text = chat_message.message.strip()
    mem       = memory.load_memory_variables({})

    # ------------------------------------------------------------------ #
    # 1) If the bot previously asked “Do you want strategies?” …
    # ------------------------------------------------------------------ #
    if mem.get(STATE_FLAG):
        intent = detect_intent(user_text)
        if intent == "VIEW_WITH_STRATEGY":             # user said yes or asked for strategies
            prompt = strategy_prompt(mem[LAST_VIEW])
            raw    = call_openrouter(prompt)

            sector_summary = extract_sector_summary(raw)
            strategies     = parse_strategies(raw)
            if len(strategies) < 3:
                raise HTTPException(500, "LLM returned fewer than 3 strategies.")

            summary_md = build_response_summary(strategies)
            charts     = generate_plotly_charts(strategies)

            # reset flag
            memory.save_context({}, {STATE_FLAG: False})

            return {
                "sector_view_summary": sector_summary,
                "response": summary_md,
                "strategies": strategies,
                "charts": {k: f.to_dict() for k, f in charts.items()},
            }

        # user did NOT confirm → continue normal chat
        normal_reply = call_openrouter(user_text)
        memory.save_context({"input": user_text}, {"output": normal_reply, STATE_FLAG: False})
        return {"response": normal_reply, "strategies": [], "charts": {}}

    # ------------------------------------------------------------------ #
    # 2) Fresh message – classify intent
    # ------------------------------------------------------------------ #
    intent = detect_intent(user_text)

    if intent == "VIEW_WITH_STRATEGY":
        # user both shares a view and explicitly asks for strategies
        prompt         = strategy_prompt(user_text)
        raw            = call_openrouter(prompt)
        sector_summary = extract_sector_summary(raw)
        strategies     = parse_strategies(raw)
        if len(strategies) < 3:
            raise HTTPException(500, "LLM returned fewer than 3 strategies.")

        summary_md = build_response_summary(strategies)
        charts     = generate_plotly_charts(strategies)

        return {
            "sector_view_summary": sector_summary,
            "response": summary_md,
            "strategies": strategies,
            "charts": {k: f.to_dict() for k, f in charts.items()},
        }

    elif intent == "VIEW_NO_STRATEGY":
        # store view, ask if they want strategies
        memory.save_context(
            {"input": user_text},
            {LAST_VIEW: user_text, STATE_FLAG: True}
        )
        follow_up_prompt = view_follow_up_prompt(user_text)
        bot_reply        = call_openrouter(follow_up_prompt)
        return {"response": bot_reply, "strategies": [], "charts": {}}

    else:
        # simple conversation
        normal_reply = call_openrouter(user_text)
        memory.save_context({"input": user_text}, {"output": normal_reply})
        return {"response": normal_reply, "strategies": [], "charts": {}}

# -----------------------------------------------------------------------
@app.get("/")
def read_root():
    return {"message": "Trading Chatbot Backend (Intent-aware)"}
