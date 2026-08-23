from typing import Dict, Any, Optional, List
from datetime import datetime
from app.data.structured_data import structured_db
from app.auth.access_control import UserContext
from app.config import SNAPSHOT_TIME_STR

class DataLookupTool:
    """
    Tool 2 of Minimum Requirements: Structured-data lookup or calculation.
    Queries accounts, orders, tickets, and calculates fees/credits/SLAs.
    """
    def __init__(self):
        self.db = structured_db
        self.reference_time = datetime.strptime(SNAPSHOT_TIME_STR, "%Y-%m-%d %H:%M")

    def lookup_order(self, order_id: str, user: UserContext) -> Dict[str, Any]:
        """Fetch details and calculate status metrics for an order."""
        order = self.db.get_order(order_id, user)
        if not order:
            return {
                "found": False,
                "error": f"Order {order_id} not found or you do not have permission to view it."
            }

        # Calculate time metrics
        booked_at = datetime.strptime(order["booked_at"], "%Y-%m-%d %H:%M")
        mins_since_booking = (self.reference_time - booked_at).total_seconds() / 60.0

        account = self.db.get_account(order["account_id"], user) or {}
        
        return {
            "found": True,
            "order": order,
            "account_name": account.get("account_name", ""),
            "plan": account.get("plan", ""),
            "mins_since_booking": round(mins_since_booking, 1),
            "reference_snapshot_time": SNAPSHOT_TIME_STR
        }

    def lookup_ticket(self, ticket_id: str, user: UserContext) -> Dict[str, Any]:
        """Fetch details and historical context for a ticket."""
        ticket = self.db.get_ticket(ticket_id, user)
        if not ticket:
            return {
                "found": False,
                "error": f"Ticket {ticket_id} not found or you do not have permission to view it."
            }

        account = self.db.get_account(ticket["account_id"], user) or {}

        # Flag historical resolution reliability
        hist_resolution = ticket.get("historical_resolution", "")
        reliability_warning = None
        if hist_resolution:
            reliability_warning = (
                "HISTORICAL CONTEXT WARNING: Historical ticket resolutions are context only "
                "and may contain incorrect or outdated guidance. Do not use as authoritative policy."
            )

        return {
            "found": True,
            "ticket": ticket,
            "account_name": account.get("account_name", ""),
            "plan": account.get("plan", ""),
            "historical_resolution_warning": reliability_warning
        }

    def calculate_cancellation_fee(self, order_id: str, user: UserContext) -> Dict[str, Any]:
        """Calculates order cancellation eligibility and fee."""
        ord_res = self.lookup_order(order_id, user)
        if not ord_res["found"]:
            return ord_res

        order = ord_res["order"]
        account_id = order["account_id"]
        status = order["status"].upper()
        mins_since_booking = ord_res["mins_since_booking"]

        # Check special customer agreement terms
        is_northstar = (account_id == "ACCT-001")
        
        fee_inr = 0
        can_cancel = True
        explanation = ""

        if status == "DRAFT":
            fee_inr = 0
            can_cancel = True
            explanation = "DRAFT shipments may be cancelled at any time with no fee."

        elif status == "BOOKED":
            if is_northstar:
                fee_inr = 0
                can_cancel = True
                explanation = (
                    "Northstar Logistics Enterprise Agreement (Section 2) waives all cancellation fees "
                    "for BOOKED shipments prior to pickup, regardless of booking time. Fee is INR 0."
                )
            elif mins_since_booking <= 30:
                fee_inr = 0
                can_cancel = True
                explanation = f"Cancelled within 30 minutes of booking ({mins_since_booking:.0f} mins ago). Fee is INR 0."
            else:
                fee_inr = 250
                can_cancel = True
                explanation = (
                    f"Cancelled more than 30 minutes after booking ({mins_since_booking:.0f} mins ago). "
                    "Standard SOP v4 charges INR 250 cancellation fee."
                )

        elif status == "PICKED_UP":
            can_cancel = False
            fee_inr = 0
            explanation = "Shipment is already PICKED_UP. Cannot cancel. Must use Return-to-Origin workflow."

        elif status == "DELIVERED":
            can_cancel = False
            fee_inr = 0
            explanation = "Shipment is already DELIVERED. Cannot cancel."

        return {
            "order_id": order_id,
            "account_id": account_id,
            "status": status,
            "can_cancel": can_cancel,
            "cancellation_fee_inr": fee_inr,
            "explanation": explanation,
            "overridden_by_agreement": is_northstar and status == "BOOKED"
        }

    def calculate_service_credit(self, order_id: str, delay_hours: float, carrier_fault: bool, customer_fault: bool, user: UserContext) -> Dict[str, Any]:
        """Calculates failed-pickup service credit eligibility and amount."""
        ord_res = self.lookup_order(order_id, user)
        if not ord_res["found"]:
            return ord_res

        order = ord_res["order"]
        account_id = order["account_id"]
        fee_inr = order.get("shipment_fee_inr", 0.0)

        # Agreement specific rules
        is_lumenworks = (account_id == "ACCT-002")
        is_northstar = (account_id == "ACCT-001")

        eligible = False
        credit_amount_inr = 0.0
        explanation = ""

        if not carrier_fault:
            explanation = "Not eligible for service credit: Delay was not due to carrier fault."
        elif customer_fault:
            explanation = "Not eligible for service credit: Customer-caused issue detected."
        else:
            if is_lumenworks:
                # LumenWorks Contract: > 4 hours delay threshold, fixed INR 300
                if delay_hours > 4.0:
                    eligible = True
                    credit_amount_inr = 300.0
                    explanation = (
                        f"Eligible under LumenWorks Service Agreement (Section 3): Pickup delay is {delay_hours:.1f} hours (>4 hrs). "
                        "Fixed credit amount of INR 300 applies."
                    )
                else:
                    explanation = f"Not eligible under LumenWorks Agreement: Delay is {delay_hours:.1f} hours, which does not exceed the required 4-hour threshold."
            else:
                # Standard SOP v4: > 2 hours delay threshold, lower of INR 500 or 10% fee
                if delay_hours > 2.0:
                    eligible = True
                    standard_calc = min(500.0, 0.10 * fee_inr)
                    credit_amount_inr = standard_calc
                    explanation = (
                        f"Eligible under Cancellation & Service Credit SOP v4 (Section 2): Pickup delay is {delay_hours:.1f} hours (>2 hrs). "
                        f"Credit is lower of INR 500 or 10% of shipment fee (INR {fee_inr}) = INR {credit_amount_inr:.2f}."
                    )
                    
                    if is_northstar and credit_amount_inr > 0:
                        explanation += " Note: Northstar monthly aggregate credit cap is INR 5,000."
                else:
                    explanation = f"Not eligible under SOP v4: Delay is {delay_hours:.1f} hours, which does not exceed the default 2-hour threshold."

        requires_manager_approval = credit_amount_inr > 1000.0

        return {
            "order_id": order_id,
            "account_id": account_id,
            "delay_hours": delay_hours,
            "carrier_fault": carrier_fault,
            "customer_fault": customer_fault,
            "eligible": eligible,
            "credit_amount_inr": credit_amount_inr,
            "requires_manager_approval": requires_manager_approval,
            "explanation": explanation
        }

data_lookup_tool = DataLookupTool()
