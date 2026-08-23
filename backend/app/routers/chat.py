from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.auth.access_control import UserContext, MOCK_USERS
from app.agent.agent import agent_instance
from app.tools.actions import action_tool

router = APIRouter(prefix="/api/chat", tags=["Chat & Actions"])

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "CUST-ACCT-001"
    chat_history: Optional[List[Dict[str, str]]] = []

class ActionConfirmationRequest(BaseModel):
    confirmation_token: str
    user_id: Optional[str] = "CUST-ACCT-001"

def _resolve_user(user_id: str) -> UserContext:
    for u in MOCK_USERS:
        if u["user_id"] == user_id:
            return UserContext(**u)
    # Default to Northstar customer if unknown
    return UserContext(**MOCK_USERS[0])

@router.get("/users")
def get_mock_users():
    """Returns list of mock users for the frontend role selector."""
    return {"users": MOCK_USERS}

@router.post("")
def chat_endpoint(req: ChatRequest):
    """
    Primary chat endpoint for natural language requests.
    Supports customer-facing & internal user contexts.
    """
    user = _resolve_user(req.user_id)
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    res = agent_instance.process_message(
        user_message=req.message.strip(),
        user=user,
        chat_history=req.chat_history
    )
    return res

@router.post("/confirm-action")
def confirm_action_endpoint(req: ActionConfirmationRequest):
    """
    Executes state-changing action after explicit user confirmation token is provided.
    """
    user = _resolve_user(req.user_id)
    result = action_tool.execute_confirmed_action(req.confirmation_token, user)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Action confirmation failed."))
    return result
