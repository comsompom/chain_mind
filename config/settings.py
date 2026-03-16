"""Load env and constants for ChainMind."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
_root = Path(__file__).resolve().parent.parent
load_dotenv(_root / ".env")

# Chain
RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:8545")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "")

# HSP (PayFi)
HSP_URL = os.getenv("HSP_URL", "https://hsp.hashkey.chain")
HSP_API_KEY = os.getenv("HSP_API_KEY", "")

# App
FLASK_ENV = os.getenv("FLASK_ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

# Data (demo)
DB_PATH = _root / "data" / "chainmind.db"
