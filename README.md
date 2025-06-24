# TradeGPT

TradeGPT is a modular, AI-powered trading strategy chatbot. It leverages large language models (LLMs) to provide users with actionable, data-driven trading strategies based on their market views. The backend is built with FastAPI and supports both OpenRouter and Hugging Face LLM APIs, while the frontend offers a clean chat interface using Streamlit. The project is organized for easy extension and maintainability.

## Features
- Conversational chat interface for trading queries
- LLM-powered strategy generation (OpenRouter or Hugging Face)
- Visualizes strategy stats with charts
- Modular backend (config, memory, parsing, charts, LLM client)


## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/kaushalkuma-r/TradeGPT.git
cd TradeGPT
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
    Add the api keys in an .env file

### 5. Run the backend server
```bash
# For OpenRouter
venv/bin/uvicorn backend/main_openrouter:app --reload --host 0.0.0.0 --port 8000

# For Hugging Face 
venv/bin/uvicorn backend/main_hf:app --reload --host 0.0.0.0 --port 8000
```

### 6. Run the frontend server
```bash
venv/bin/streamlit run frontend/app.py --server.port 8501
```

### 7. Access the app
Open your browser and go to: [http://localhost:8501](http://localhost:8501)

## License
MIT