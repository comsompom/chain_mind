"""Load env and constants for ChainMind."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (and cwd so "flask run" from repo root finds .env)
_root = Path(__file__).resolve().parent.parent
load_dotenv(_root / ".env")
load_dotenv(Path.cwd() / ".env")  # override when running from project root

# Chain (HashKey Chain Testnet for hackathon – DeFi track)
# https://docs.hashkeychain.net/docs/Developer-QuickStart
RPC_URL = os.getenv("RPC_URL", "https://testnet.hsk.xyz")
CHAIN_ID = int(os.getenv("CHAIN_ID", "133"))  # HashKey Chain Testnet = 133
CHAIN_DISPLAY_NAME = os.getenv("CHAIN_DISPLAY_NAME", "HashKey Chain Testnet")
NATIVE_SYMBOL = os.getenv("NATIVE_SYMBOL", "HSK")  # HashKey Chain native token
WALLET_ADDRESS = (os.getenv("WALLET_ADDRESS") or "").strip()

# HSP (PayFi) / HashKey Sandbox (exchange account)
HSP_URL = os.getenv("HSP_URL", "https://hsp.hashkey.chain")
HSP_API_KEY = os.getenv("HSP_API_KEY", "")
HSP_SECRET = os.getenv("HSP_SECRET", "")  # Required for sandbox account balance/trades

# App
FLASK_ENV = os.getenv("FLASK_ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

# Data (demo)
DB_PATH = _root / "data" / "chainmind.db"
