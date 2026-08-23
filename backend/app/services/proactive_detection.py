from typing import List, Dict, Any
from datetime import datetime
from app.data.structured_data import structured_db
from app.auth.access_control import UserContext
from app.config import SNAPSHOT_TIME_STR

class ProactiveIssueDetector:
    """
    Addresses Client Problem 1: Proactive Issue Detection
    Scans tickets, orders, and known product issues to surface urgent & recurring patterns.
    """
    def __init__(self):
        self.db = structured_db
        self.snapshot_time = datetime.strptime(SNAPSHOT_TIME_STR, "%Y-%m-%d %H:%M")

    def run_proactive_analysis(self, user: UserContext) -> Dict[str, Any]:
        if not user.is_internal:
            return {"error": "Unauthorized: Proactive Issue Detection is restricted to internal operations personnel."}

        all_tickets = self.db.list_tickets(user)
        all_orders = self.db.list_orders(user)

        alerts = []

        # 1. Check SLA Breaches & Risks
        sla_alerts = self._check_sla_status(all_tickets)
        alerts.extend(sla_alerts)

        # 2. Check Recurring Product Bug Clusters (e.g., KI-208 Bulk Upload)
        product_bug_alerts = self._check_known_issue_clusters(all_tickets)
        alerts.extend(product_bug_alerts)

        # 3. Check Order Pickup Delays & Carrier Fault Patterns
        order_alerts = self._check_order_anomalies(all_orders)
        alerts.extend(order_alerts)

        # 4. Check Security & Credential Incident Alerts
        sec_alerts = self._check_security_incidents(all_tickets)
        alerts.extend(sec_alerts)

        # Sort alerts by severity (P1 Critical > P2 High > P3 Normal)
        severity_order = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4}
        alerts.sort(key=lambda x: severity_order.get(x["severity"], 5))

        return {
            "snapshot_reference_time": SNAPSHOT_TIME_STR,
            "total_alerts_detected": len(alerts),
            "alerts": alerts,
            "summary": {
                "critical_count": sum(1 for a in alerts if a["severity"] == "CRITICAL"),
                "high_count": sum(1 for a in alerts if a["severity"] == "HIGH"),
                "medium_count": sum(1 for a in alerts if a["severity"] == "MEDIUM")
            }
        }

    def _check_sla_status(self, tickets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        alerts = []
        for tkt in tickets:
            if tkt["status"].lower() != "open":
                continue

            created_at = datetime.strptime(tkt["created_at"], "%Y-%m-%d %H:%M")
            mins_open = (self.snapshot_time - created_at).total_seconds() / 60.0

            account = self.db.get_account(tkt["account_id"], UserContext(role="internal", user_id="sys", user_name="sys", is_internal=True)) or {}
            acc_name = account.get("account_name", tkt["account_id"])
            plan = account.get("plan", "Standard")

            # SLA Targets in minutes
            # Northstar custom SLA: P1 15m, P2 1h
            # Standard Enterprise: P1 30m, P2 2h
            # Growth: P1 2h (120m)
            target_mins = 1440 # default
            if account.get("account_id") == "ACCT-001":
                # Northstar Enterprise custom agreement
                if "all shipment creation is failing" in tkt["subject"].lower() or "http 500" in tkt["description"].lower():
                    target_mins = 15 # P1
            elif plan == "Enterprise":
                target_mins = 30 # P1 default
            elif plan == "Growth":
                target_mins = 120 # P1 default

            if mins_open > target_mins:
                breach_amount = mins_open - target_mins
                alerts.append({
                    "alert_id": f"ALT-SLA-{tkt['ticket_id']}",
                    "title": f"SLA Target Breached: Ticket {tkt['ticket_id']} ({acc_name})",
                    "severity": "CRITICAL",
                    "category": "SLA_BREACH",
                    "description": f"Ticket '{tkt['subject']}' has been open for {mins_open:.0f} mins (Target: {target_mins} mins). Breached by {breach_amount:.0f} mins.",
                    "impact": f"{acc_name} ({plan} Plan). Dedicated CSM: {account.get('csm', 'Unassigned')}.",
                    "recommended_action": f"Immediately escalate ticket {tkt['ticket_id']} to Tier 2 Support and notify CSM {account.get('csm')}.",
                    "ticket_id": tkt["ticket_id"],
                    "account_id": tkt["account_id"]
                })
        return alerts

    def _check_known_issue_clusters(self, tickets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        alerts = []
        bulk_fail_tickets = [t for t in tickets if "bulk" in t["subject"].lower() or "csv" in t["description"].lower()]
        
        if len(bulk_fail_tickets) >= 1:
            alerts.append({
                "alert_id": "ALT-KI-208",
                "title": "Recurring Product Defect: CSV Bulk Upload Failures (KI-208)",
                "severity": "HIGH",
                "category": "PRODUCT_BUG",
                "description": f"Multiple customers (including {', '.join(set(t['account_id'] for t in bulk_fail_tickets))}) reporting CSV upload failures on large files.",
                "impact": "Customers experiencing intermittent failures on CSV uploads > 3,000 rows due to active product bug KI-208.",
                "recommended_action": "Inform affected customers of official workaround: split CSV files into batches under 3,000 rows.",
                "related_tickets": [t["ticket_id"] for t in bulk_fail_tickets]
            })
        return alerts

    def _check_order_anomalies(self, orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        alerts = []
        for ord_rec in orders:
            if ord_rec["carrier_fault"] and ord_rec["status"] == "BOOKED":
                alerts.append({
                    "alert_id": f"ALT-ORD-FAIL-{ord_rec['order_id']}",
                    "title": f"Unfulfilled Order Carrier Fault: {ord_rec['order_id']}",
                    "severity": "HIGH",
                    "category": "CARRIER_ANOMALY",
                    "description": f"Order {ord_rec['order_id']} ({ord_rec['carrier']}) pickup window ended without pickup. Carrier accepted fault.",
                    "impact": f"Customer account {ord_rec['account_id']}. Shipment fee: INR {ord_rec['shipment_fee_inr']}.",
                    "recommended_action": "Issue proactive service credit calculation and contact carrier dispatch for immediate re-pickup.",
                    "order_id": ord_rec["order_id"],
                    "account_id": ord_rec["account_id"]
                })
        return alerts

    def _check_security_incidents(self, tickets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        alerts = []
        for tkt in tickets:
            if "api key" in tkt["subject"].lower() or "security" in tkt["description"].lower():
                alerts.append({
                    "alert_id": f"ALT-SEC-{tkt['ticket_id']}",
                    "title": f"CRITICAL SECURITY INCIDENT: {tkt['subject']}",
                    "severity": "CRITICAL",
                    "category": "SECURITY",
                    "description": f"Potential credential exposure reported in ticket {tkt['ticket_id']}: '{tkt['description']}'.",
                    "impact": "Account credential compromised. Per Support Policy v3 Section 2, security incidents are classified as P1 Critical.",
                    "recommended_action": "Immediately revoke exposed production API key, rotate credentials, and notify security lead.",
                    "ticket_id": tkt["ticket_id"],
                    "account_id": tkt["account_id"]
                })
        return alerts

proactive_detector = ProactiveIssueDetector()
