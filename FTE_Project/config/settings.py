"""
Centralized configuration management for FTE Agent
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
VAULT_DIR = BASE_DIR / "vault"

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Application Settings
APP_NAME = os.getenv("APP_NAME", "FTE_Agent")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Vault Paths
VAULT_INBOX = VAULT_DIR / "inbox"
VAULT_PROCESSED = VAULT_DIR / "processed"
VAULT_ACTIONS = VAULT_DIR / "actions"
VAULT_LOGS = VAULT_DIR / "logs"

# Ensure directories exist
for path in [VAULT_INBOX, VAULT_PROCESSED, VAULT_ACTIONS, VAULT_LOGS]:
    path.mkdir(parents=True, exist_ok=True)

# Agent Configuration
AGENT_TEMPERATURE = 0.7
AGENT_MAX_TOKENS = 2000
AGENT_TIMEOUT = 60  # seconds

# Action Configuration
ACTION_EXPIRY_HOURS = 24
AUTO_APPROVE_LOW_RISK = False

def validate_config():
    """Validate required configuration"""
    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY not found. "
            "Please copy .env.example to .env and add your API key."
        )
    return True
