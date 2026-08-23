from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.auth.access_control import UserContext, MOCK_USERS
from app.services.proactive_detection import proactive_detector
from app.data.structured_data import structured_db

router = APIRouter(prefix="/api/dashboard", tags=["Proactive Operations Dashboard"])

def _resolve_user(user_id: str) -> UserContext:
    for u in MOCK_USERS:
        if u["user_id"] == user_id:
            return UserContext(**u)
    return UserContext(**MOCK_USERS[4]) # Default to Rohit (Internal)

@router.get("/proactive-issues")
def get_proactive_issues(user_id: Optional[str] = "AGENT-ROHIT"):
    """
    Client Problem 1: Proactive Issue Detection
    Returns real-time alerts for SLA breaches, recurring bugs, carrier anomalies, security risks.
    Restricted to internal users.
    """
    user = _resolve_user(user_id)
    if not user.is_internal:
        raise HTTPException(status_code=403, detail="Access Denied: Proactive Issue Detection dashboard is restricted to internal ParcelPilot operations staff.")

    return proactive_detector.run_proactive_analysis(user)

@router.get("/tickets")
def get_tickets(user_id: Optional[str] = "AGENT-ROHIT"):
    user = _resolve_user(user_id)
    tickets = structured_db.list_tickets(user)
    return {"tickets": tickets}

@router.get("/orders")
def get_orders(user_id: Optional[str] = "AGENT-ROHIT"):
    user = _resolve_user(user_id)
    orders = structured_db.list_orders(user)
    return {"orders": orders}
