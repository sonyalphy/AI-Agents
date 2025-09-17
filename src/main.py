from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .agent import Agent, get_default_tools
import os

app = FastAPI(title="AWS AI Agent Starter")

# CORS (dev-friendly)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    used_tools: list[str]
    session_id: str

# In-memory sessions (for demo). Replace with Redis/DB in real apps.
SESSIONS: dict[str, dict] = {}

def get_agent(session_id: str) -> Agent:
    session = SESSIONS.setdefault(session_id, {"memory": {}, "history": []})
    return Agent(session=session, tools=get_default_tools())

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/agent/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    agent = get_agent(req.session_id)
    reply, used = agent.handle(req.message)
    return ChatResponse(reply=reply, used_tools=used, session_id=req.session_id)

# Serve static React (CDN) UI (no build tools needed)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.isdir(static_dir):
    os.makedirs(static_dir, exist_ok=True)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
