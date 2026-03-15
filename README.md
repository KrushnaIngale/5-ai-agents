# Multi-Agent AI Chatbot Practical

This repo contains only the files needed for the practical:

- 5 AI agents
- A sequential AI pipeline
- A frontend showing accountability of all agents
- One chatbot UI for the final response
- Gemini and Groq support
- Optional LangGraph execution

## Deliverables

1. Create random 5 AI agents
2. Create a front end taking accountability of all the AI agents
3. Create a pipeline of AI agents
4. Deploy all in one UI in the form of a chatbot

## Agents Used

1. Prompt Analyzer
2. Research Agent
3. Logic / Reasoning Agent
4. Content Generator
5. Output Formatter

## Architecture

User -> Streamlit Chatbot UI -> Pipeline Controller -> 5 AI Agents -> Final Response

## Required Files

```text
.
|-- .streamlit/
|   |-- config.toml
|   `-- secrets.toml.example
|-- app.py
|-- multi_agent_chatbot/
|   |-- __init__.py
|   |-- config.py
|   |-- pipeline.py
|   |-- providers.py
|   `-- ui.py
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- .env
`-- README.md
```

## Local Setup

1. Install Python 3.10 or later.
2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Update `.env` with a working API key and model.

Example:

```env
DEFAULT_PROVIDER=groq
GEMINI_KEY=
GEMINI_MODEL=gemini-2.5-flash
GROQ_KEY=your_real_groq_key
GROQ_MODEL=llama-3.1-8b-instant
```

## Run Locally

```bash
python -m streamlit run app.py
```

Open `http://localhost:8501`

## Deploy

Recommended path: Streamlit Community Cloud.

1. Push this folder to a GitHub repository.
2. In Streamlit Community Cloud, create a new app from that repo.
3. Set the main file path to `app.py`.
4. Add your secrets in the app settings using the same keys shown in `.streamlit/secrets.toml.example`.
5. Deploy.

Example secrets:

```toml
DEFAULT_PROVIDER="groq"
GEMINI_KEY=""
GEMINI_MODEL="gemini-2.5-flash"
GROQ_KEY="your_real_groq_key"
GROQ_MODEL="llama-3.1-8b-instant"
```

## UI Features

- Chat-style Streamlit interface
- Final answer shown in chatbot form
- Agent accountability section for all 5 agents
- Optional LangGraph toggle for the same pipeline

## 2-Week Practical Plan

Week 1:

- Learn the selected API
- Test each agent separately
- Tune prompts
- Validate the pipeline order

Week 2:

- Improve UI clarity
- Add better error handling
- Test with real prompts
- Deploy the chatbot