import streamlit as st
import requests
import plotly.graph_objects as go
import base64

# === Background image setup ===
def set_background(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Call the background setter
# set_background("background.jpg")

# === Streamlit App ===
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
            chart_keys = list(message["charts"].keys())
            for i in range(0, len(chart_keys), 3):
                cols = st.columns(min(3, len(chart_keys) - i))
                for j, key in enumerate(chart_keys[i:i+3]):
                    with cols[j]:
                        st.subheader(key.replace("_", " ").title())
                        fig = go.Figure(message["charts"][key])
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
            for i in range(0, len(chart_keys), 3):
                cols = st.columns(min(3, len(chart_keys) - i))
                for j, key in enumerate(chart_keys[i:i+3]):
                    with cols[j]:
                        st.subheader(key.replace("_", " ").title())
                        fig = go.Figure(charts[key])
                        st.plotly_chart(fig, use_container_width=True)

        st.session_state.messages.append({
            "role": "assistant",
            "content": bot_response,
            "charts": charts
        })

    except requests.exceptions.RequestException as e:
        st.error(f"Error contacting backend: {e}")
