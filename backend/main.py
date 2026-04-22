from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.langgraph_agent import run_agent
from tools.tools import log_interaction

app = FastAPI(title="AI-First CRM Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = ""
    text: str = ""


class InteractionRequest(BaseModel):
    hcp_name: str = ""
    interaction_type: str = "general"
    notes: str = ""


@app.get("/")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/chat")
def chat(payload: ChatRequest) -> Dict[str, Any]:
    user_input = payload.message or payload.text
    return run_agent(user_input)


@app.post("/interactions/log")
def interactions_log(payload: InteractionRequest) -> Dict[str, Any]:
    return log_interaction(payload.model_dump())
