from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from langchain.memory import ConversationBufferMemory
from utils.charts import generate_plotly_charts
from utils.parsing import (
    extract_sector_summary,
    parse_strategies,
    build_response_summary,
)
from utils.llm_client import call_openrouter, detect_intent
from utils.prompts import view_follow_up_prompt, strategy_prompt

app = FastAPI()
session_states = {}

class SessionState:
    def __init__(self):
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="input",
            output_key="output",
            return_messages=True
        )
        self.last_view = ""
        self.awaiting_confirmation = False

class ChatMessage(BaseModel):
    message: str
    session_id: str = None  # Add session ID in request

@app.post("/chat")
async def chat(chat_message: ChatMessage):
    user_text = chat_message.message.strip()
    
    # Get or create session
    session_id = chat_message.session_id or str(uuid4())
    if session_id not in session_states:
        session_states[session_id] = SessionState()
    
    state = session_states[session_id]
    mem = state.memory.load_memory_variables({})

    # 1) Handle strategy confirmation flow
    if state.awaiting_confirmation:
        intent = detect_intent(user_text)
        if intent == "VIEW_WITH_STRATEGY":
            prompt = strategy_prompt(state.last_view)
            raw = call_openrouter(prompt)
            
            sector_summary = extract_sector_summary(raw)
            strategies = parse_strategies(raw)
            if len(strategies) < 3:
                raise HTTPException(500, "LLM returned fewer than 3 strategies.")

            summary_md = build_response_summary(strategies)
            charts = generate_plotly_charts(strategies)
            charts_dict = {k: v.to_dict() for k, v in charts.items()}  # Fixed variable name
            
            # Reset flag and save context
            state.awaiting_confirmation = False
            state.memory.save_context(
                {"input": user_text}, 
                {"output": "Generated trading strategies"}
            )
            
            return {
                "session_id": session_id,
                "sector_view_summary": sector_summary,
                "response": summary_md,
                "strategies": strategies,
                "charts": charts_dict  # Use correct variable
            }

        # Handle non-confirmation
        normal_reply = call_openrouter(user_text)
        state.memory.save_context(
            {"input": user_text}, 
            {"output": normal_reply}
        )
        state.awaiting_confirmation = False
        return {
            "session_id": session_id,
            "response": normal_reply,
            "strategies": [],
            "charts": {}
        }

    # 2) Handle fresh messages
    intent = detect_intent(user_text)
    
    if intent == "VIEW_WITH_STRATEGY":
        prompt = strategy_prompt(user_text)
        raw = call_openrouter(prompt)
        sector_summary = extract_sector_summary(raw)
        strategies = parse_strategies(raw)
        if len(strategies) < 3:
            raise HTTPException(500, "LLM returned fewer than 3 strategies.")

        summary_md = build_response_summary(strategies)
        charts = generate_plotly_charts(strategies)
        charts_dict = {k: v.to_dict() for k, v in charts.items()}

        state.memory.save_context(
            {"input": user_text},
            {"output": "Provided strategies"}
        )
        return {
            "session_id": session_id,  # Added session ID
            "sector_view_summary": sector_summary,
            "response": summary_md,
            "strategies": strategies,
            "charts": charts_dict  # Use correct variable
        }

    elif intent == "VIEW_NO_STRATEGY":
        state.last_view = user_text
        state.awaiting_confirmation = True
        follow_up = call_openrouter(view_follow_up_prompt(user_text))
        
        state.memory.save_context(
            {"input": user_text},
            {"output": follow_up}
        )
        
        return {
            "session_id": session_id,
            "response": follow_up,
            "strategies": [],
            "charts": {}
        }
    else:
        # Simple conversation
        normal_reply = call_openrouter(user_text)
        state.memory.save_context(  # Use session memory instead of global
            {"input": user_text},
            {"output": normal_reply}
        )
        return {
            "session_id": session_id,  # Added session ID
            "response": normal_reply,
            "strategies": [],
            "charts": {}
        }

@app.get("/")
def read_root():
    return {"message": "Trading Chatbot Backend (Session-aware)"}