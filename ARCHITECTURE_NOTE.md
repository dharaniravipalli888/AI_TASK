# 🏛️ Architecture Note — ParcelPilot AI Support & Operations Platform

## 1. Agent Design

The system implements a **multi-agent hybrid architecture** capable of orchestrating multi-step reasoning over unstructured documentation and structured operational data.

```
┌──────────────────────────────────────────────────────────────────┐
│                      React Frontend (Vite)                       │
│  ┌───────────────────────┐   ┌────────────────────────────────┐  │
│  │ Dual-Context Chat UI  │   │ Proactive Operations Dashboard │  │
│  └───────────┬───────────┘   └───────────────┬────────────────┘  │
└──────────────┼───────────────────────────────┼───────────────────┘
               │ HTTP / API Requests           │
               ▼                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend API                         │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │           Data-Layer Access Control Middleware             │  │
│  └────────────────────────────┬───────────────────────────────┘  │
│                               ▼                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                ParcelPilot AI Agent Loop                   │  │
│  │   ┌───────────────────┬───────────────────┬─────────────┐  │  │
│  │   │ Tool 1: Doc Search│ Tool 2: Data      │ Tool 3:     │  │  │
│  │   │ (TF-IDF & Rank)   │ Lookup & Calc     │ State Action│  │  │
│  │   └───────────────────┴───────────────────┴─────────────┘  │  │
│  └────────────────────────────┬───────────────────────────────┘  │
│                               ▼                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │        Source Precedence & Conflict Resolution Engine      │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Key Components:
- **LLM Engine**: Powered by Groq API running `llama-3.3-70b-versatile` with low temperature (`0.1`) for strict factual adherence.
- **Deterministic Multi-Step Solver Fallback**: Includes a fallback solver ensuring 100% availability even during external API outages or rate limits.
- **System Prompts (`prompts.py`)**: Tailored system prompts enforcing role scoping, time snapshot reference (`2026-08-16 11:00 Asia/Kolkata`), source precedence, and confirmation requirements.

---

## 2. Tool Design

The agent is equipped with **three distinct tools**:

### Tool 1: Document Search / Retrieval (`document_search.py`)
- Performs TF-IDF vector similarity and keyword-boosted retrieval across policy documents, SOPs, product guides, and customer enterprise agreements.
- Automatically ranks results by **source precedence score** (1 = Signed Agreement, 2 = Current Policy v3, 3 = SOP v4, 4 = Product Ops, 9 = Deprecated).
- Enforces data privacy by excluding contracts belonging to other accounts for customer users.

### Tool 2: Structured-Data Lookup & Calculation (`data_lookup.py`)
- Queries accounts, orders, and support tickets via Pandas data structures.
- Performs domain calculations:
  - **Cancellation Fee Calculation**: Evaluates booking timestamp against snapshot time, order status (`DRAFT`, `BOOKED`, `PICKED_UP`, `DELIVERED`), and customer-specific contract waivers (e.g. Northstar waiver).
  - **Service Credit Engine**: Evaluates pickup delay duration, carrier fault, customer fault, SOP limits (INR 500 / 10%), and customer contract rules (e.g. LumenWorks 4-hour threshold & INR 300 fixed credit).

### Tool 3: State-Changing Action & Confirmation Safeguard (`actions.py`)
- Prepares state-changing actions (`create_escalation`, `update_ticket`, `create_followup_task`).
- Generates a unique, cryptographically random `confirmation_token` (e.g., `CONFIRM-A1B2C3D4`).
- **Confirmation Flow**: Returns a pending action card to the UI. The action is ONLY executed when the user explicitly clicks "Confirm & Execute".

---

## 3. Document and Structured-Data Handling

- **PDF Ingestion (`document_loader.py`)**: Uses `pdfplumber` to extract document text and split into logical sections. Adds metadata tags: `status` (`CURRENT` vs `DEPRECATED`), `precedence_rank`, and `account_id` mapping.
- **Excel Structured Data (`structured_data.py`)**: Loads `ParcelPilot_Assessment_Data.xlsx` into memory DataFrames. Timestamp parsing is anchored strictly to the dataset snapshot reference time: `2026-08-16 11:00 Asia/Kolkata`.
- **Access Control Scoping (`access_control.py`)**: Data privacy is enforced **at the code level** before queries reach data models. Customer users cannot retrieve records where `account_id != user.account_id`.

---

## 4. Source Reliability and Conflict Handling (Problem 2)

To prevent confidently incorrect answers, the platform implements a dedicated **Source Resolver (`source_resolver.py`)**:

```
Source Authority Hierarchy:
1. Signed Customer Enterprise Agreements (Rank 1)  [HIGHEST]
2. 01_Support_Policy_v3_CURRENT.pdf (Rank 2)
3. 03_Cancellation_and_Service_Credit_SOP_v4.pdf (Rank 3)
4. 04_Product_Operations_Guide_and_Known_Issues.pdf (Rank 4)
9. 02_Support_Policy_v2_DEPRECATED.pdf (Rank 9)    [DO NOT USE]
10. Historical Ticket Resolutions (Rank 10)         [CONTEXT ONLY - MAY BE WRONG]
```

### Conflict Resolution Strategy:
- **Contract Override**: When a signed customer agreement exists (e.g. Northstar or LumenWorks), its clauses automatically supersede general support policies and SOPs.
- **Deprecation Guard**: Deprecated documents (v2) are explicitly excluded from authoritative answers.
- **Historical Ticket Warning**: Historical tickets (such as TKT-450 charging Northstar a fee, or TKT-451 claiming a 3K row limit) are flagged as **unreliable context** and explicitly overridden by current agreements.

---

## 5. Major Technical Trade-Offs

| Decision | Chosen Approach | Trade-Off / Rationale |
|----------|-----------------|------------------------|
| **LLM Provider** | Groq Llama 3.3 70B | Fast inference speed (~500 tokens/sec) and free tier, with fallback rule-solver for reliability. |
| **Document Retrieval** | TF-IDF + Keyword Boosting | Lightweight, zero external vector DB dependencies, instant execution, exact keyword precision for policy terms. |
| **Access Control** | Hardcoded Data-Layer Filters + Mock Auth | Complies with assessment requirement to scope at the data layer without overhead of building full OAuth/JWT infrastructure. |
| **State Persistence** | In-Memory DataFrames & Tokens | Fast setup for assessment demonstration; state resets on server restart (production would use PostgreSQL/Redis). |
