from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import ChatMessageHistory
import plotly.graph_objs as go

load_dotenv()

app = FastAPI()

# Updated memory setup for compatibility
memory = ConversationBufferMemory(
    return_messages=True,
    chat_memory=ChatMessageHistory()
)

HUGGING_FACE_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HUGGING_FACE_API_TOKEN = os.getenv("HUGGING_FACE_API_TOKEN")

headers = {"Authorization": f"Bearer {HUGGING_FACE_API_TOKEN}"}

class ChatMessage(BaseModel):
    message: str

def generate_plotly_charts(strategies):
    charts = {}

    charts['popularity'] = go.Figure([go.Bar(x=[s['name'] for s in strategies], y=[s['popularity'] for s in strategies])])
    charts['popularity'].update_layout(title='Strategy Popularity (%)', xaxis_title='Strategy', yaxis_title='Popularity')

    charts['avg_return'] = go.Figure([go.Bar(x=[s['name'] for s in strategies], y=[s['avg_return'] for s in strategies])])
    charts['avg_return'].update_layout(title='Average Return (%)', xaxis_title='Strategy', yaxis_title='Return')

    charts['sharpe_ratio'] = go.Figure([go.Bar(x=[s['name'] for s in strategies], y=[s['sharpe_ratio'] for s in strategies])])
    charts['sharpe_ratio'].update_layout(title='Sharpe Ratio', xaxis_title='Strategy', yaxis_title='Sharpe Ratio')

    charts['win_rate'] = go.Figure([go.Bar(x=[s['name'] for s in strategies], y=[s['win_rate'] for s in strategies])])
    charts['win_rate'].update_layout(title='Win Rate (%)', xaxis_title='Strategy', yaxis_title='Win Rate')

    charts['max_drawdown'] = go.Figure([go.Bar(x=[s['name'] for s in strategies], y=[s['max_drawdown'] for s in strategies])])
    charts['max_drawdown'].update_layout(title='Max Drawdown (%)', xaxis_title='Strategy', yaxis_title='Drawdown')

    charts['profit_factor'] = go.Figure([go.Bar(x=[s['name'] for s in strategies], y=[s['profit_factor'] for s in strategies])])
    charts['profit_factor'].update_layout(title='Profit Factor', xaxis_title='Strategy', yaxis_title='Profit Factor')

    charts['volatility'] = go.Figure([go.Bar(x=[s['name'] for s in strategies], y=[s['volatility'] for s in strategies])])
    charts['volatility'].update_layout(title='Volatility (%)', xaxis_title='Strategy', yaxis_title='Volatility')

    charts['risk_reward_ratio'] = go.Figure([go.Bar(x=[s['name'] for s in strategies], y=[s['risk_reward_ratio'] for s in strategies])])
    charts['risk_reward_ratio'].update_layout(title='Risk-Reward Ratio', xaxis_title='Strategy', yaxis_title='Risk-Reward Ratio')

    charts['trade_frequency'] = go.Figure([go.Bar(x=[s['name'] for s in strategies], y=[s['trade_frequency'] for s in strategies])])
    charts['trade_frequency'].update_layout(title='Trade Frequency (trades/month)', xaxis_title='Strategy', yaxis_title='Trade Frequency')

    return charts

@app.post("/chat")
async def chat(chat_message: ChatMessage):
    context = memory.load_memory_variables({})
    combined_prompt = f"{context['history']}\nUser: {chat_message.message}"

    prompt = f"""
You are a highly knowledgeable trading assistant. A user has a market view or belief as follows:
"{chat_message.message}"

Your job is to recommend at least 3 unique, well-justified **short- to medium-term trading strategies** aligned with this view. Each strategy should be distinct (not overlapping), used in real-world trading, and should not be long-term investment suggestions.

For each strategy, provide:
- Strategy: [Name of the strategy]
- Explanation: [What this strategy is, how it works, and how it relates to the user's view. Include key instruments used and rationale. Be clear and concise.]
- Popularity: [X]%
- Average Return: [Y]%
- Sharpe Ratio: [Z]
- Win Rate: [W]%
- Max Drawdown: [D]%
- Profit Factor: [P]
- Volatility: [V]%
- Risk-Reward Ratio: [R]
- Trade Frequency: [T] trades/month
---

Only return structured strategies in this exact format. Ensure that each strategy is well-formed, detailed, and not repeated. Avoid generic suggestions and instead recommend actionable trade setups.
"""

    try:
        response = requests.post(HUGGING_FACE_API_URL, headers=headers, json={"inputs": prompt})
        print(response)
        response.raise_for_status()
        llm_response = response.json()
        # print(llm_response)
        raw_text = llm_response[0]['generated_text']

        strategies = []
        parts = raw_text.split('---')
        for part in parts:
            if "Strategy:" in part:
                try:
                    name = part.split("Strategy:")[1].split("Explanation:")[0].strip()
                    explanation = part.split("Explanation:")[1].split("Popularity:")[0].strip()
                    popularity = int(part.split("Popularity:")[1].split("%") [0].strip())
                    avg_return = float(part.split("Average Return:")[1].split("%") [0].strip())
                    sharpe = float(part.split("Sharpe Ratio:")[1].split("Win Rate:")[0].strip())
                    win_rate = float(part.split("Win Rate:")[1].split("%") [0].strip())
                    drawdown = float(part.split("Max Drawdown:")[1].split("%") [0].strip())
                    profit_factor = float(part.split("Profit Factor:")[1].split("Volatility:")[0].strip())
                    volatility = float(part.split("Volatility:")[1].split("%") [0].strip())
                    risk_reward = float(part.split("Risk-Reward Ratio:")[1].split("Trade Frequency:")[0].strip())
                    trade_freq = float(part.split("Trade Frequency:")[1].split("trades")[0].strip())

                    strategies.append({
                        "name": name,
                        "explanation": explanation,
                        "popularity": popularity,
                        "avg_return": avg_return,
                        "sharpe_ratio": sharpe,
                        "win_rate": win_rate,
                        "max_drawdown": drawdown,
                        "profit_factor": profit_factor,
                        "volatility": volatility,
                        "risk_reward_ratio": risk_reward,
                        "trade_frequency": trade_freq
                    })
                except (IndexError, ValueError):
                    continue

        # if len(strategies) < 3:
        #     return {"response": "Could not generate enough trading strategies.", "strategies": [], "charts": {}}

        response_summary = ""
        for s in strategies:
            response_summary += f"\n### {s['name']}\n"
            response_summary += f"- **Explanation**: {s['explanation']}\n"
            response_summary += f"- **Popularity**: {s['popularity']}%\n"
            response_summary += f"- **Average Return**: {s['avg_return']}%\n"
            response_summary += f"- **Sharpe Ratio**: {s['sharpe_ratio']}\n"
            response_summary += f"- **Win Rate**: {s['win_rate']}%\n"
            response_summary += f"- **Max Drawdown**: {s['max_drawdown']}%\n"
            response_summary += f"- **Profit Factor**: {s['profit_factor']}\n"
            response_summary += f"- **Volatility**: {s['volatility']}%\n"
            response_summary += f"- **Risk-Reward Ratio**: {s['risk_reward_ratio']}\n"
            response_summary += f"- **Trade Frequency**: {s['trade_frequency']} trades/month\n"


        memory.save_context({"input": chat_message.message}, {"output": response_summary})

        charts = generate_plotly_charts(strategies)
        print(response_summary)
        return {
            "response": response_summary.strip(),
            "strategies": strategies,
            "charts": {k: fig.to_dict() for k, fig in charts.items()}
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling Hugging Face API: {e}")
    except (KeyError, IndexError) as e:
        raise HTTPException(status_code=500, detail=f"Error processing LLM response: {e}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Trading Chatbot Backend"}
