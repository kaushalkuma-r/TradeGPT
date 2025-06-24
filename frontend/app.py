import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📈 Trading Strategy Chatbot")
st.caption("An interactive assistant for strategy ideas — powered by FastAPI & Hugging Face")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "charts" in message and message["charts"]:
            strategy_names = [s["name"] for s in message["strategies"]]
            color_map = {name: px.colors.qualitative.Plotly[i % 10] for i, name in enumerate(strategy_names)}

            # 🎨 Legend
            st.markdown("### 🎨 Strategy Color Legend")
            legend_cols = st.columns(len(strategy_names))
            for i, name in enumerate(strategy_names):
                with legend_cols[i]:
                    st.markdown(f"<div style='background-color:{color_map[name]};width:20px;height:20px;display:inline-block;border-radius:3px'></div> &nbsp; {name}", unsafe_allow_html=True)

            # 📊 Charts
            chart_keys = list(message["charts"].keys())
            for i in range(0, len(chart_keys), 3):  # 3 charts per row
                cols = st.columns(min(3, len(chart_keys) - i))
                for j, key in enumerate(chart_keys[i:i+3]):
                    with cols[j]:
                        st.subheader(key.replace("_", " ").title())
                        fig = go.Figure(message["charts"][key])
                        for trace in fig.data:
                            strategy = trace.name if hasattr(trace, "name") else None
                            if strategy and strategy in color_map:
                                trace.marker.color = color_map[strategy]
                            else:
                                trace.marker.color = list(color_map.values())[j % len(color_map)]
                        st.plotly_chart(fig, use_container_width=True)

# Handle new user input
if prompt := st.chat_input("What's your market view or investment interest?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        response = requests.post("http://127.0.0.1:8000/chat", json={"message": prompt})
        response.raise_for_status()
        data = response.json()

        bot_response = data.get("response", "Sorry, I couldn't get a response.")
        charts = data.get("charts", {})
        sector_summary = data.get("sector_view_summary", None)

        with st.chat_message("assistant"):
            if sector_summary:
                st.markdown("#### 🧠 Sector & View Summary")
                st.info(sector_summary)

            st.markdown("#### 📊 Strategy Recommendations")
            st.markdown(bot_response)

            chart_keys = list(charts.keys())
            for i in range(0, len(chart_keys), 3):  # 3 charts per row
                cols = st.columns(min(3, len(chart_keys) - i))
                for j, key in enumerate(chart_keys[i:i+3]):
                    with cols[j]:
                        st.subheader(key.replace("_", " ").title())
                        fig = go.Figure(charts[key])
                        st.plotly_chart(fig, use_container_width=True)

        st.session_state.messages.append({
            "role": "assistant",
            "content": f"#### 🧠 Sector & View Summary\n{sector_summary}\n\n#### 📊 Strategy Recommendations\n{bot_response}",
            "charts": charts
        })

    except requests.exceptions.RequestException as e:
        st.error(f"Error contacting backend: {e}")
