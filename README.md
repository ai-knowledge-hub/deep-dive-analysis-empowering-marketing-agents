# Empowering Marketing AI Agents — Starter Pack

Build AI agents that *empower users to achieve their goals*, not just drive conversions. This starter pack turns the concepts from the article **"The Next Chapter in Marketing — From Campaign Optimization to Human Empowerment"** into running code.

## ✨ What you get
- A lightweight **agent framework** (planning · memory · tools · personality).
- Pluggable **LLM providers**: `dummy` (no external calls), `openai`, or `ollama`.
- Example **personas**: Learning Navigator, Fitness Coach.
- Minimal **web API** (FastAPI) and CLI demos.
- Simple **integrations** (analytics, notifications, CRM stubs).
- Empowerment-first **metrics** and tests.

> Works offline by default using the `dummy` LLM so you can run examples immediately.

## 🚀 Quick Start

```bash
git clone https://github.com/your-org/empowering-marketing-agents.git
cd empowering-marketing-agents

# 1) Create a virtualenv (recommended)
python -m venv .venv && source .venv/bin/activate

# 2) Install deps
pip install -r requirements.txt

# 3) Copy env and choose an LLM provider (dummy | openai | ollama)
cp .env.example .env
# default is LLM_PROVIDER=dummy (no API keys needed)

# 4) Run the Learning Navigator demo (CLI)
python examples/learning_navigator_demo.py

# 5) Start the web API (http://127.0.0.1:8000/docs)
uvicorn examples.web_interface_demo:app --reload
```

### Optional: Use OpenAI or Ollama
- **OpenAI**: set `LLM_PROVIDER=openai` and `OPENAI_API_KEY=...` in `.env`.
- **Ollama**: set `LLM_PROVIDER=ollama` and (optionally) `OLLAMA_BASE_URL=http://localhost:11434`.
  - Example model: `llama3` or `mistral`

## 📦 Repository Structure
```
empowering-marketing-agents/
├── README.md
├── requirements.txt
├── setup.py
├── .env.example
├── docs/
│   ├── architecture.md
│   ├── deployment.md
│   └── examples.md
├── src/
│   └── empowering_agents/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── agent.py
│       │   ├── memory.py
│       │   ├── planning.py
│       │   └── tools.py
│       ├── personalities/
│       │   ├── __init__.py
│       │   ├── learning_navigator.py
│       │   └── fitness_coach.py
│       ├── integrations/
│       │   ├── __init__.py
│       │   ├── analytics.py
│       │   ├── crm.py
│       │   └── notifications.py
│       └── utils/
│           ├── __init__.py
│           ├── llm_utils.py
│           └── evaluation.py
├── examples/
│   ├── learning_navigator_demo.py
│   ├── fitness_coach_demo.py
│   ├── multi_agent_demo.py
│   └── web_interface_demo.py
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   └── test_personalities.py
├── deployment/
│   ├── docker-compose.yml
│   └── Dockerfile
└── notebooks/
    └── README.md
```

## 🧠 Design Principles
- **Empowerment over engagement**: optimize for goal achievement and user growth.
- **Pragmatic**: simple, hackable code; no heavy dependencies required.
- **Pluggable**: swap LLM providers and integrations without code changes.

## 🧪 Run tests
```bash
pytest -q
```

## 🧱 Roadmap
- Add vector memory and retrieval.
- Add more tool adapters (Google Calendar, Notion, HubSpot).
- Add DSPy-based planning variant.

---

**License:** MIT


### Using compiled planner hints
- Run `python experiments/dspy_compile_demo.py` to generate artifacts.
- The runtime planners will automatically read `experiments/.artifacts/compiled_hints.json` (or set `COMPILED_HINTS_PATH`).
- Hints are injected into the planning context to steer JSON structure and step quality without breaking offline mode.


## 🗓 Google Calendar Tool (optional)
This pack ships with a real Google Calendar adapter. It stays dormant unless you enable it.

**Enable it:**
1. Create an OAuth 2.0 Client ID (Desktop) in Google Cloud and download the JSON as `client_secret.json`.
2. Place it at the path in `.env` (`GOOGLE_CLIENT_SECRETS=./client_secret.json`).
3. In `.env`, set `GOOGLE_CALENDAR_ENABLED=true` and update `GOOGLE_TOKEN_PATH` if desired.
4. First run will open a browser for consent; token is cached.

**Try it:**
```bash
python examples/calendar_demo.py
```
Or pass a `schedule_block` in the `context` to any agent call to request a real event creation.
