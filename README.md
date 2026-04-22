# AI-First CRM HCP Module

This repository contains a full-stack implementation of the Round-1 Task-1 assignment for an AI-first CRM Log Interaction screen.

## Tech Stack

- Frontend: React + Vite + Redux Toolkit + Tailwind CSS
- Backend: FastAPI (Python)
- Agent Orchestration: LangGraph
- LLM: Groq (`gemma2-9b-it` via `langchain-groq`)
- Database: PostgreSQL

## Project Structure

- `frontend/`: UI for structured interaction logging and conversational logging
- `backend/`: API endpoints, LangGraph agent, SQL tool functions

## Core Features

- Structured Form Logging:
  - HCP name, interaction type, datetime, notes, topics, outcome, follow-up
  - Posts to backend endpoint `POST /interactions/log`
- Conversational Logging:
  - User chats with the assistant in natural language
  - Backend routes request through LangGraph and executes one of five tools

## AI-First Flow (How It Works)

This module is AI-first because chat is not just a side assistant; it actively drives CRM data capture.

1. User sends natural language input to `POST /chat`.
2. LangGraph classifies intent and extracts structured fields (HCP name, type, notes, topics, follow-up, outcome).
3. Agent executes a tool action (log/edit/info/summarize/follow-up/compliance).
4. Backend also extracts sentiment from each interaction text.
5. Frontend uses returned `payload` + `result` to auto-fill the structured form.

Result: reps can speak naturally first, then review/edit a pre-filled compliant form before final logging.

## LangGraph Agent Tools

1. `log_interaction`
2. `edit_interaction`
3. `get_hcp_info`
4. `summarize_interaction`
5. `suggest_followup`
6. `compliance_check`

These tools are defined in `backend/tools/tools.py` and orchestrated through the graph in `backend/agent/langgraph_agent.py`.

## Quick Fix Plan Implemented

- ✅ Compliance tool added: checks chat/log text for potential PII/PHI and risky medical-claim language.
- ✅ Sentiment extraction added: each agent response includes sentiment label and score.
- ✅ Chat to form auto-fill added: chat output now updates form fields (`hcpName`, `interactionType`, `notes`, `topics`, `outcome`, `followUp`).
- ✅ README improved with AI-first architecture explanation and updated tool list.

## Setup

### 1. Backend

From repository root:

```powershell
& .\\.venv\\Scripts\\python.exe -m pip install fastapi uvicorn langchain langgraph langchain-groq python-dotenv psycopg2-binary
```

Create/update `backend/.env`:

```env
GROQ_API_KEY=your_groq_key
DB_NAME=crm
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

Run backend:

```powershell
Set-Location backend
& ..\\.venv\\Scripts\\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Frontend

```powershell
npm --prefix frontend install
npm --prefix frontend run dev
```

Open the Vite URL shown in terminal (for example `http://localhost:5177`).

Optional `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## API Endpoints

- `GET /` health endpoint
- `POST /chat` conversational agent endpoint
- `POST /interactions/log` structured form logging endpoint

## Notes

- The backend starts even if DB connection is unavailable and returns clear DB error messages for write operations.
- The frontend uses Google Inter font as required.
