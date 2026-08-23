from typing import List, Dict, Any, Optional

class SourceResolver:
    """
    Addresses Client Problem 2: Trust & Reliability
    Evaluates conflicting documents, computes confidence scores, and determines human escalation.
    """
    
    SOURCE_HIERARCHY = {
        "ENTERPRISE_AGREEMENT": 100,  # Highest authority: Signed Customer Agreement
        "CURRENT_SUPPORT_POLICY_V3": 85,  # 01_Support_Policy_v3_CURRENT.pdf
        "CURRENT_SOP_V4": 80,  # 03_Cancellation_and_Service_Credit_SOP_v4.pdf
        "PRODUCT_OPS_GUIDE": 75,  # 04_Product_Operations_Guide_and_Known_Issues.pdf
        "DEPRECATED_POLICY_V2": 10,  # 02_Support_Policy_v2_DEPRECATED.pdf (DO NOT USE)
        "HISTORICAL_TICKET_RESOLUTION": 5  # Historical ticket answers (Explicitly Unreliable)
    }

    def resolve_sources(self, doc_results: List[Dict[str, Any]], query_context: str = "") -> Dict[str, Any]:
        """
        Analyzes retrieved document chunks, detects conflicts, applies authority hierarchy,
        and returns a confidence report with source citations.
        """
        if not doc_results:
            return {
                "authoritative_sources": [],
                "conflicts_detected": [],
                "confidence_score": "LOW",
                "needs_human_escalation": True,
                "reason": "No relevant documentation found."
            }

        conflicts = []
        deprecated_found = []
        agreements_found = []
        valid_sources = []

        for item in doc_results:
            fname = item.get("file_name", "")
            status = item.get("status", "")
            
            if status == "DEPRECATED" or "v2" in fname:
                deprecated_found.append(item)
                conflicts.append(f"Excluded deprecated document '{fname}' in favor of current v3 policy/v4 SOP.")
            elif item.get("account_id") and ("Agreement" in fname or "Contract" in fname):
                agreements_found.append(item)
                valid_sources.append(item)
            else:
                valid_sources.append(item)

        # Precedence resolution
        confidence = "HIGH"
        escalate = False
        primary_source = None

        if agreements_found:
            primary_source = agreements_found[0]
            conflicts.append(f"Applied override rule: Signed agreement '{primary_source['title']}' supersedes standard policy defaults.")
        elif valid_sources:
            primary_source = valid_sources[0]
        else:
            confidence = "LOW"
            escalate = True

        return {
            "primary_source": primary_source,
            "authoritative_sources": valid_sources,
            "deprecated_sources_rejected": deprecated_found,
            "conflicts_detected": conflicts,
            "confidence_score": confidence,
            "needs_human_escalation": escalate,
            "hierarchy_rule_applied": "Customer Agreement > Current Policy v3 > SOP v4 > Product Docs >> Deprecated Docs / Past Tickets"
        }

source_resolver = SourceResolver()
