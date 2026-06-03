import os
from pathlib import Path
from typing import List

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DB_PATH = BASE_DIR / "heartbleed.db"

# Exports
EXPORTS_DIR = BASE_DIR / "exports"
REPORTS_DIR = EXPORTS_DIR / "reports"

# Ensure directories exist
EXPORTS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# Network Settings
DEFAULT_TIMEOUT = 10
MAX_RETRIES = 3
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (HeartBleed OSINT v0.2)"

# Correlation Thresholds
MATCH_USERNAME_EXACT = 30
MATCH_USERNAME_SIMILAR = 20
MATCH_WEBSITE = 15
MATCH_LOCATION = 10
MATCH_BIO = 20
MATCH_IMAGE = 25

# Confidence Levels
CONFIDENCE_VERY_HIGH = 81
CONFIDENCE_HIGH = 61
CONFIDENCE_MEDIUM = 31
CONFIDENCE_LOW = 0
