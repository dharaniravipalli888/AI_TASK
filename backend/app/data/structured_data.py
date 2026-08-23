import os
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config import DATA_DIR, SNAPSHOT_TIME_STR
from app.auth.access_control import UserContext, check_account_access

class StructuredDataLoader:
    def __init__(self, excel_path: str = None):
        if excel_path is None:
            excel_path = os.path.join(DATA_DIR, "ParcelPilot_Assessment_Data.xlsx")
        self.excel_path = excel_path
        self.accounts_df = pd.DataFrame()
        self.orders_df = pd.DataFrame()
        self.tickets_df = pd.DataFrame()
        self.snapshot_time = datetime.strptime(SNAPSHOT_TIME_STR, "%Y-%m-%d %H:%M")
        self.load_data()

    def load_data(self):
        """Loads all Excel sheets into memory DataFrames."""
        xls = pd.ExcelFile(self.excel_path)
        
        if "accounts" in xls.sheet_names:
            self.accounts_df = pd.read_excel(xls, "accounts").fillna("")
        if "orders" in xls.sheet_names:
            self.orders_df = pd.read_excel(xls, "orders").fillna("")
        if "tickets" in xls.sheet_names:
            self.tickets_df = pd.read_excel(xls, "tickets").fillna("")

    # --- Account Methods ---
    def get_account(self, account_id: str, user: UserContext) -> Optional[Dict[str, Any]]:
        """Fetch account record if user is authorized."""
        if not check_account_access(user, account_id):
            return None
        match = self.accounts_df[self.accounts_df["account_id"] == account_id]
        if match.empty:
            return None
        return match.iloc[0].to_dict()

    def get_all_accounts(self, user: UserContext) -> List[Dict[str, Any]]:
        """Fetch accounts list scoped to user's authorization."""
        records = self.accounts_df.to_dict(orient="records")
        if user.is_internal:
            return records
        return [r for r in records if r.get("account_id") == user.account_id]

    # --- Order Methods ---
    def get_order(self, order_id: str, user: UserContext) -> Optional[Dict[str, Any]]:
        """Fetch specific order details with access control verification."""
        match = self.orders_df[self.orders_df["order_id"] == order_id]
        if match.empty:
            return None
        record = match.iloc[0].to_dict()
        if not check_account_access(user, record["account_id"]):
            return None
        return record

    def list_orders(self, user: UserContext, account_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List orders scoped to user permissions."""
        df = self.orders_df.copy()
        
        # Enforce account scope for customer users
        if not user.is_internal:
            df = df[df["account_id"] == user.account_id]
        elif account_id:
            df = df[df["account_id"] == account_id]

        if status:
            df = df[df["status"].str.upper() == status.upper()]

        return df.to_dict(orient="records")

    # --- Ticket Methods ---
    def get_ticket(self, ticket_id: str, user: UserContext) -> Optional[Dict[str, Any]]:
        """Fetch ticket by ID with access control."""
        match = self.tickets_df[self.tickets_df["ticket_id"] == ticket_id]
        if match.empty:
            return None
        record = match.iloc[0].to_dict()
        if not check_account_access(user, record["account_id"]):
            return None
        return record

    def list_tickets(self, user: UserContext, account_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tickets scoped to user permissions."""
        df = self.tickets_df.copy()

        if not user.is_internal:
            df = df[df["account_id"] == user.account_id]
        elif account_id:
            df = df[df["account_id"] == account_id]

        if status:
            df = df[df["status"].str.lower() == status.lower()]

        return df.to_dict(orient="records")

    def search_all_data(self, query: str, user: UserContext) -> Dict[str, Any]:
        """Search across structured tables based on text query."""
        query_lower = query.lower()
        results = {"orders": [], "tickets": [], "account": None}

        # Match order IDs or carrier names
        orders = self.list_orders(user)
        for ord_rec in orders:
            if (query_lower in str(ord_rec.get("order_id", "")).lower() or
                query_lower in str(ord_rec.get("carrier", "")).lower() or
                query_lower in str(ord_rec.get("notes", "")).lower()):
                results["orders"].append(ord_rec)

        # Match ticket IDs or subject/description
        tickets = self.list_tickets(user)
        for tkt_rec in tickets:
            if (query_lower in str(tkt_rec.get("ticket_id", "")).lower() or
                query_lower in str(tkt_rec.get("subject", "")).lower() or
                query_lower in str(tkt_rec.get("description", "")).lower()):
                results["tickets"].append(tkt_rec)

        # If user account is customer, attach account info
        if user.account_id:
            results["account"] = self.get_account(user.account_id, user)

        return results

# Global singleton loader instance
structured_db = StructuredDataLoader()
