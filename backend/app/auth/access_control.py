from typing import Optional, List
from pydantic import BaseModel

class UserContext(BaseModel):
    role: str  # "customer" or "internal"
    user_id: str  # e.g., "USER-NORTHSTAR", "AGENT-ROHIT"
    user_name: str  # e.g., "Northstar Admin", "Rohit (Support Tier 2)"
    account_id: Optional[str] = None  # Required for customer role, e.g., "ACCT-001"
    account_name: Optional[str] = None
    plan: Optional[str] = None
    is_internal: bool = False

# Mock users available for selector in UI
MOCK_USERS = [
    {
        "user_id": "CUST-ACCT-001",
        "role": "customer",
        "user_name": "Northstar Logistics (Enterprise)",
        "account_id": "ACCT-001",
        "account_name": "Northstar Logistics",
        "plan": "Enterprise",
        "is_internal": False
    },
    {
        "user_id": "CUST-ACCT-002",
        "role": "customer",
        "user_name": "LumenWorks (Growth)",
        "account_id": "ACCT-002",
        "account_name": "LumenWorks",
        "plan": "Growth",
        "is_internal": False
    },
    {
        "user_id": "CUST-ACCT-003",
        "role": "customer",
        "user_name": "Beacon Retail (Standard)",
        "account_id": "ACCT-003",
        "account_name": "Beacon Retail",
        "plan": "Standard",
        "is_internal": False
    },
    {
        "user_id": "CUST-ACCT-004",
        "role": "customer",
        "user_name": "Axis Labs (Enterprise)",
        "account_id": "ACCT-004",
        "account_name": "Axis Labs",
        "plan": "Enterprise",
        "is_internal": False
    },
    {
        "user_id": "AGENT-ROHIT",
        "role": "internal",
        "user_name": "Rohit (Support Operations Lead)",
        "account_id": None,
        "account_name": "ParcelPilot Internal",
        "plan": "Internal",
        "is_internal": True
    },
    {
        "user_id": "AGENT-MAYA",
        "role": "internal",
        "user_name": "Maya (Tier 2 Support Specialist)",
        "account_id": None,
        "account_name": "ParcelPilot Internal",
        "plan": "Internal",
        "is_internal": True
    }
]

def check_account_access(user: UserContext, target_account_id: str) -> bool:
    """Enforces data privacy at the code layer."""
    if user.is_internal:
        return True
    if user.account_id and user.account_id == target_account_id:
        return True
    return False

def filter_by_user_access(user: UserContext, items: List[dict], account_key: str = "account_id") -> List[dict]:
    """Filters a list of records based on user's authorized account context."""
    if user.is_internal:
        return items
    return [item for item in items if item.get(account_key) == user.account_id]
