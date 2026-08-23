# 🚀 ParcelPilot AI Support & Operations Platform

> First-Round AI Agent Assessment for CalQuity — AI Engineer Position

ParcelPilot AI is an enterprise multi-agent customer support and proactive operations platform designed for B2B logistics management. It features **dual chatbot contexts** (Customer-Facing & Authorized Internal Staff), **data-layer access control**, **multi-step reasoning**, **source reliability precedence resolution**, **state-changing action confirmation safeguards**, and a **Proactive Issue Detection Dashboard**.

---

## 🌟 Key Features

1. **Dual Chatbot Contexts**:
   - **Customer-Facing**: Scoped strictly to the authenticated customer's account (`ACCT-001`, `ACCT-002`, etc.). Privacy enforced at the data layer.
   - **Internal Operations**: Full cross-account visibility for ParcelPilot support staff to investigate tickets, track SLAs, and manage operational anomalies.
2. **Three Core Agent Tools**:
   - 🔍 **Document Search & Retrieval**: TF-IDF similarity search over policies, contracts, SOPs, and product guides with source hierarchy ranking.
   - 📊 **Structured Data Lookup & Calculations**: Pandas query engine over accounts, orders, and tickets, calculating time-elapsed, cancellation fees, and service credit eligibility.
   - ⚡ **State-Changing Actions**: Prepares ticket escalations, status updates, and follow-up tasks.
3. **Confirmation Before Actions Safeguard**:
   - Any state-changing action generates a unique `confirmation_token` and requires explicit user confirmation before execution.
4. **Source Reliability & Conflict Resolution (Client Problem 2)**:
   - Resolves conflicts using strict precedence rules: `Signed Customer Agreement > Support Policy v3 > Cancellation SOP v4 > Product Ops Guide >> Deprecated Docs / Historical Tickets`.
5. **Proactive Issue Detection Dashboard (Client Problem 1)**:
   - Real-time command center identifying P1 SLA breaches (e.g. Northstar 15-min target), recurring product bug clusters (KI-208 CSV upload bug), carrier pickup anomalies, and security credential exposure alerts.

---

## 🛠️ Repository Structure

```
├── backend/
│   ├── app/
│   │   ├── agent/             # Agent execution loop & prompts
│   │   ├── auth/              # Mock auth & data-layer access control
│   │   ├── data/              # Document loader (PDFs) & Structured DB (Excel)
│   │   ├── routers/           # FastAPI chat & dashboard routers
│   │   ├── services/          # Proactive issue detector & source resolver
│   │   ├── tools/             # Agent tools (Doc search, Data lookup, Actions)
│   │   ├── config.py          # Environment & source hierarchy config
│   │   └── main.py            # FastAPI entry point
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/        # UserSelector, ChatInterface, ToolIndicator, ProactiveDashboard, ActionConfirmationModal
│   │   ├── App.jsx            # Main app container & context switcher
│   │   ├── index.css          # Glassmorphism design system
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── data/                      # Candidate Data Pack (PDFs & Excel workbook)
├── README.md
├── ARCHITECTURE_NOTE.md
├── PRODUCT_NOTE.md
└── AI_TOOL_USAGE.md
```

---

## ⚡ Quickstart Setup & Local Run Instructions

### 1. Environment Setup

Copy `.env` into the root directory (or `backend/.env`):
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Backend Setup & Server Run

```bash
# Create and activate python virtual environment
python -m venv venv
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r backend/requirements.txt

# Launch FastAPI backend server on port 8000
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
Backend API will be live at `http://127.0.0.1:8000`. API Docs available at `http://127.0.0.1:8000/docs`.

### 3. Frontend Setup & Local Run

In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
Frontend application will be live at `http://localhost:3000`.

---

## 🧪 Testing Example Assessment Queries

You can test the system using the user selector dropdown in the UI:

1. **Northstar Cancellation Fee Waiver Test**:
   - Query: *"Can Northstar cancel ORD-1001 without a cancellation fee? Explain why."*
   - Result: Confirms INR 0 fee because Northstar's signed agreement waives fees on BOOKED shipments prior to pickup, overriding general SOP defaults. Flags historical ticket TKT-450 as unreliable historical context.

2. **LumenWorks Service Credit Threshold Test**:
   - Select User: `LumenWorks (Growth)`
   - Query: *"A pickup is 3 hours late because of carrier fault. Should I get a service credit?"*
   - Result: Answers No for LumenWorks (requires >4 hrs per contract), but Yes for standard policy (>2 hrs threshold).

3. **State-Changing Action Confirmation Test**:
   - Query: *"Escalate ticket TKT-501 due to HTTP 500 outage"*
   - Result: Displays a tokenized Action Confirmation Modal before executing the escalation.

4. **Proactive Issue Detection Test**:
   - Switch role to `Rohit (Support Operations Lead)` and click **Proactive Dashboard**.
   - Result: Surfaces active P1 SLA breaches, KI-208 bug clusters, and recommended ops actions.
