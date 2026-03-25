from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.langgraph_agent import run_agent
from tools.tools import log_interaction


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Interaction(BaseModel):
    text: str


class InteractionLog(BaseModel):
    hcp_name: str
    interaction_type: str
    notes: str = ""

@app.get("/")
def home():
    return {"message": "Backend running 🚀"}

@app.post("/chat")
def chat(interaction: Interaction):
    result = run_agent(interaction.text)
    return {"response": result}


@app.post("/interactions/log")
def create_interaction(interaction: InteractionLog):
    result = log_interaction(interaction.model_dump())
    return {"response": result}