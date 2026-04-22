import json
import os
import re
from typing import Any, Dict, Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

from tools.tools import (
    compliance_check,
    edit_interaction,
    extract_sentiment,
    get_hcp_info,
    log_interaction,
    suggest_followup,
    summarize_interaction,
)

load_dotenv()

try:
    from langchain_groq import ChatGroq
except ModuleNotFoundError:
    ChatGroq = None


class AgentState(TypedDict, total=False):
    user_input: str
    action: Literal[
        "log_interaction",
        "edit_interaction",
        "get_hcp_info",
        "summarize_interaction",
        "suggest_followup",
        "compliance_check",
    ]
    payload: Dict[str, Any]
    result: Dict[str, Any]


llm = None
if ChatGroq and os.getenv("GROQ_API_KEY"):
    llm = ChatGroq(model_name="gemma2-9b-it", api_key=os.getenv("GROQ_API_KEY"))


def _safe_json(text: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{[\s\S]*\}", text or "")
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                return fallback
        return fallback


def _extract_payload(user_input: str) -> Dict[str, Any]:
    fallback = {
        "hcp_name": "",
        "interaction_type": "general",
        "notes": user_input,
        "id": None,
        "new_notes": "",
        "name": "",
        "text": user_input,
        "topics": [],
        "follow_up": "",
        "outcome": "",
    }

    if llm is None:
        return fallback

    prompt = f"""
You are an extraction engine for a healthcare CRM agent.
Extract fields from the user request and return strict JSON only.

User input: {user_input}

Return JSON with keys:
- hcp_name (string)
- interaction_type (string)
- notes (string)
- id (number or null)
- new_notes (string)
- name (string)
- text (string)
- topics (array of strings)
- follow_up (string)
- outcome (string)
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return _safe_json(getattr(response, "content", ""), fallback)


def _select_action(user_input: str, payload: Dict[str, Any]) -> str:
    text = (user_input or "").lower()

    # Heuristic fallback so the graph still works when LLM is unavailable.
    if "edit" in text or "update" in text:
        return "edit_interaction"
    if "summarize" in text or "summary" in text:
        return "summarize_interaction"
    if "follow" in text or "next step" in text:
        return "suggest_followup"
    if "compliance" in text or "policy" in text or "risk" in text:
        return "compliance_check"
    if "hcp" in text or "doctor" in text or "specialization" in text:
        return "get_hcp_info"
    if "log" in text or payload.get("hcp_name"):
        return "log_interaction"

    if llm is None:
        return "summarize_interaction"

    prompt = f"""
Classify the user request into one action for CRM tools.
Allowed actions only:
- log_interaction
- edit_interaction
- get_hcp_info
- summarize_interaction
- suggest_followup
- compliance_check

User input: {user_input}
Payload: {json.dumps(payload)}

Return strict JSON: {{"action": "one_of_allowed_actions"}}
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    data = _safe_json(getattr(response, "content", ""), {"action": "summarize_interaction"})
    action = data.get("action", "summarize_interaction")
    if action not in {
        "log_interaction",
        "edit_interaction",
        "get_hcp_info",
        "summarize_interaction",
        "suggest_followup",
        "compliance_check",
    }:
        return "summarize_interaction"
    return action


def classify_node(state: AgentState) -> AgentState:
    user_input = state.get("user_input", "")
    payload = _extract_payload(user_input)
    action = _select_action(user_input, payload)
    return {"payload": payload, "action": action}


def execute_node(state: AgentState) -> AgentState:
    action = state.get("action", "summarize_interaction")
    payload = state.get("payload", {})
    user_input = state.get("user_input", "")

    if action == "log_interaction":
        result = log_interaction(
            {
                "hcp_name": payload.get("hcp_name", ""),
                "interaction_type": payload.get("interaction_type", "general"),
                "notes": payload.get("notes", state.get("user_input", "")),
            }
        )
    elif action == "edit_interaction":
        interaction_id = payload.get("id")
        if interaction_id in (None, ""):
            # Fallback: try to parse an id from the raw user text, e.g. "edit interaction 2 ...".
            match = re.search(r"\b(?:id\s*)?(\d+)\b", user_input.lower())
            if match:
                interaction_id = int(match.group(1))

        if isinstance(interaction_id, str) and interaction_id.isdigit():
            interaction_id = int(interaction_id)

        if interaction_id in (None, ""):
            result = {
                "status": "Please provide interaction id to edit. Example: edit interaction 2 notes updated details",
            }
        else:
            result = edit_interaction(interaction_id, payload.get("new_notes", payload.get("notes", "")))
    elif action == "get_hcp_info":
        name = payload.get("name") or payload.get("hcp_name") or "Unknown HCP"
        result = get_hcp_info(name)
    elif action == "suggest_followup":
        result = suggest_followup(payload.get("text", state.get("user_input", "")))
    elif action == "compliance_check":
        result = compliance_check(payload.get("text", state.get("user_input", "")))
    else:
        result = summarize_interaction(payload.get("text", state.get("user_input", "")))

    sentiment = extract_sentiment(payload.get("text", state.get("user_input", "")))
    result = {
        **(result or {}),
        "sentiment": sentiment.get("sentiment", "neutral"),
        "sentiment_score": sentiment.get("score", 0),
    }

    return {"result": result}


graph_builder = StateGraph(AgentState)
graph_builder.add_node("classify", classify_node)
graph_builder.add_node("execute", execute_node)
graph_builder.set_entry_point("classify")
graph_builder.add_edge("classify", "execute")
graph_builder.add_edge("execute", END)
langgraph_agent = graph_builder.compile()


def run_agent(user_input: str) -> Dict[str, Any]:
    state = langgraph_agent.invoke({"user_input": user_input})
    return {
        "action": state.get("action"),
        "payload": state.get("payload", {}),
        "result": state.get("result", {}),
    }