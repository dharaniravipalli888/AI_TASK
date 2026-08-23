import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.auth.access_control import UserContext
from app.data.structured_data import structured_db

# In-memory storage for pending action confirmations & action logs
PENDING_ACTIONS: Dict[str, Dict[str, Any]] = {}
EXECUTED_ACTIONS_LOG: List[Dict[str, Any]] = []

class ActionTool:
    """
    Tool 3 of Minimum Requirements: State-changing actions with explicit confirmation.
    """
    
    def prepare_escalation(self, ticket_id: str, reason: str, severity: str, user: UserContext) -> Dict[str, Any]:
        """Prepares a ticket escalation request requiring user confirmation."""
        ticket = structured_db.get_ticket(ticket_id, user)
        if not ticket and not user.is_internal:
            return {"success": False, "error": f"Ticket {ticket_id} not found or unauthorized."}

        token = f"CONFIRM-{uuid.uuid4().hex[:8].upper()}"

        action_payload = {
            "confirmation_token": token,
            "action_type": "CREATE_ESCALATION",
            "ticket_id": ticket_id,
            "account_id": ticket.get("account_id") if ticket else user.account_id,
            "params": {
                "ticket_id": ticket_id,
                "reason": reason,
                "severity": severity,
                "requested_by": user.user_name,
                "target_team": "Tier 2 Support / Operations"
            },
            "summary": f"Escalate ticket {ticket_id} ({severity.upper()}) to Tier 2 Operations",
            "details": f"Reason: {reason}",
            "requires_confirmation": True,
            "status": "PENDING_CONFIRMATION",
            "created_at": datetime.now().isoformat()
        }

        PENDING_ACTIONS[token] = action_payload
        return action_payload

    def prepare_ticket_update(self, ticket_id: str, new_status: str, notes: str, user: UserContext) -> Dict[str, Any]:
        """Prepares a ticket status update requiring user confirmation."""
        ticket = structured_db.get_ticket(ticket_id, user)
        if not ticket:
            return {"success": False, "error": f"Ticket {ticket_id} not found or unauthorized."}

        token = f"CONFIRM-{uuid.uuid4().hex[:8].upper()}"

        action_payload = {
            "confirmation_token": token,
            "action_type": "UPDATE_TICKET",
            "ticket_id": ticket_id,
            "account_id": ticket.get("account_id"),
            "params": {
                "ticket_id": ticket_id,
                "old_status": ticket.get("status"),
                "new_status": new_status,
                "notes": notes,
                "updated_by": user.user_name
            },
            "summary": f"Update status of {ticket_id} from '{ticket.get('status')}' to '{new_status}'",
            "details": f"Notes: {notes}",
            "requires_confirmation": True,
            "status": "PENDING_CONFIRMATION",
            "created_at": datetime.now().isoformat()
        }

        PENDING_ACTIONS[token] = action_payload
        return action_payload

    def prepare_followup_task(self, ticket_id: str, task_description: str, assigned_to: str, user: UserContext) -> Dict[str, Any]:
        """Prepares a follow-up task creation requiring user confirmation."""
        token = f"CONFIRM-{uuid.uuid4().hex[:8].upper()}"

        action_payload = {
            "confirmation_token": token,
            "action_type": "CREATE_FOLLOWUP_TASK",
            "ticket_id": ticket_id,
            "account_id": user.account_id,
            "params": {
                "ticket_id": ticket_id,
                "task_description": task_description,
                "assigned_to": assigned_to,
                "created_by": user.user_name
            },
            "summary": f"Create follow-up task for {ticket_id} assigned to {assigned_to}",
            "details": f"Task: {task_description}",
            "requires_confirmation": True,
            "status": "PENDING_CONFIRMATION",
            "created_at": datetime.now().isoformat()
        }

        PENDING_ACTIONS[token] = action_payload
        return action_payload

    def execute_confirmed_action(self, confirmation_token: str, user: UserContext) -> Dict[str, Any]:
        """Executes a previously prepared state-changing action after explicit confirmation."""
        if confirmation_token not in PENDING_ACTIONS:
            return {
                "success": False,
                "error": f"Invalid or expired confirmation token: {confirmation_token}"
            }

        action_data = PENDING_ACTIONS.pop(confirmation_token)
        action_data["status"] = "EXECUTED"
        action_data["executed_at"] = datetime.now().isoformat()
        action_data["executed_by"] = user.user_name

        EXECUTED_ACTIONS_LOG.append(action_data)

        # Apply state changes to mock in-memory DB if ticket update
        if action_data["action_type"] == "UPDATE_TICKET":
            tkt_id = action_data["params"]["ticket_id"]
            new_st = action_data["params"]["new_status"]
            # update in pandas dataframe
            df = structured_db.tickets_df
            df.loc[df["ticket_id"] == tkt_id, "status"] = new_st

        return {
            "success": True,
            "message": f"Successfully executed action: {action_data['summary']}",
            "action_details": action_data
        }

action_tool = ActionTool()
