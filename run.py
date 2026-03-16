"""Run ChainMind from project root: python run.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app import app
from config import settings

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=(settings.FLASK_ENV == "development"))
