import streamlit as st, base64, requests, plotly.graph_objects as go

# --- MUST be first Streamlit call -------------
st.set_page_config(page_title="Trading Strategy Chatbot", layout="wide")
# ----------------------------------------------

def set_background(image_file: str) -> None:
    """Cover the viewport with *image_file* while keeping content visible."""
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
            /* 1️⃣ Full-page fixed layer */
            .stApp::before {{
                content:"";
                position:fixed; inset:0;
                background:url("data:image/jpg;base64,{encoded}") center/cover no-repeat;
                z-index:-1;
            }}

            /* 2️⃣ Transparent shells */
            html, body, .stApp {{ background:transparent; }}

            /* 3️⃣ Make text & widget labels readable on dark bg */
            h1, h2, h3, h4, h5, h6,
            p, label, span, div, textarea, input, textarea,
            .stTextInput > div > div > input {{
                color:#ffffff !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# inject CSS **after** page-config
set_background("5072609.jpg")

# === Streamlit UI ===
st.title("📈 Trading Strategy Chatbot")
st.caption("An interactive assistant for discussing Trading strategies")

# … (rest of your code is unchanged) …


# === Streamlit App ===
st.set_page_config(layout="wide")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display all chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # For assistant messages, show additional elements
        if message["role"] == "assistant":
            if message.get("sector_summary"):
                st.markdown("#### 🧠 Sector & View Summary")
                st.info(message["sector_summary"])
            st.markdown(" ")
        
        # Main message content
        st.markdown(message["content"])
        
        # Show charts if they exist
        if message["role"] == "assistant" and "charts" in message and message["charts"]:
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
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    try:
        # Get response from backend
        response = requests.post("http://127.0.0.1:8000/chat", json={"message": prompt})
        response.raise_for_status()
        data = response.json()

        bot_response = data.get("response", "Sorry, I couldn't get a response.")
        charts = data.get("charts", {})
        sector_summary = data.get("sector_view_summary", None)

        # Create assistant message structure
        assistant_message = {
            "role": "assistant",
            "content": bot_response,
            "charts": charts
        }
        
        if sector_summary:
            assistant_message["sector_summary"] = sector_summary

        # Add assistant response to chat history
        st.session_state.messages.append(assistant_message)
        
        # Rerun to update the display immediately
        st.rerun()

    except requests.exceptions.RequestException as e:
        st.error(f"Error contacting backend: {e}")