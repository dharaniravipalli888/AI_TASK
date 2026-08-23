import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

# Groq API key support (check GROQ_API_KEY, groq_api, or fallback)
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("groq_api") or ""

# Reference dataset snapshot time from README sheet
SNAPSHOT_TIME_STR = "2026-08-16 11:00"
SNAPSHOT_TIMEZONE = "Asia/Kolkata"

# Source precedence ranking (1 is highest authority)
SOURCE_PRECEDENCE = {
    "enterprise_agreement": 1,  # Signed customer agreements (e.g. Northstar, LumenWorks)
    "current_policy": 2,        # 01_Support_Policy_v3_CURRENT.pdf
    "current_sop": 3,           # 03_Cancellation_and_Service_Credit_SOP_v4.pdf
    "product_ops": 4,           # 04_Product_Operations_Guide_and_Known_Issues.pdf
    "deprecated_policy": 9,     # 02_Support_Policy_v2_DEPRECATED.pdf (DO NOT USE)
    "historical_tickets": 10    # Historical ticket resolutions (Context only, may be wrong)
}
