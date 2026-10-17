import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


DATA_DIR = BASE_DIR / "data"
CRM_FILE = DATA_DIR / "crm.json"
ICP_FILE = DATA_DIR / "icp.json"

if not OPENAI_API_KEY:
    raise RuntimeError("Please provide the OPENAI_API_KEY to proceed.")
