# AWS AI Agent Starter (FastAPI + Static React UI)

Minimal **AI Agent** app with a FastAPI backend and a lightweight React (CDN) UI.
- Tools: Calculator, Memory, Echo, WebSearch (DuckDuckGo via httpx)
- Endpoint: `POST /agent/chat` with `{ session_id, message }`
- Static UI served from the backend (no Node build needed)

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

Open http://localhost:8000 and chat.

## Docker
```bash
docker build -t ai-agent .
docker run -p 8000:8000 ai-agent
```

## CI
GitHub Actions workflow runs tests and builds the Docker image.

## Demo - AI - Agent
[🎥 Watch Demo](./demo-ai-agent.mov)
