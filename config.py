"""
config.py — Configuration constants and environment variable loading.
"""

import os

# ── Telegram credentials ──────────────────────────────────────────────────────
API_ID: int = int(os.environ.get("API_ID", "0"))
API_HASH: str = os.environ.get("API_HASH", "")
BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "")
OWNER_ID: int = int(os.environ.get("OWNER_ID", "0"))

# ── Optional channel join reminder (not enforced) ─────────────────────────────
# Set to a channel username/ID to show a soft join reminder, or leave empty.
CHANNEL_USERNAME: str = os.environ.get("CHANNEL_USERNAME", "")

# ── SQLite database file path ─────────────────────────────────────────────────
DB_PATH: str = os.environ.get("DB_PATH", "ubot.db")

# ── Access level constants ────────────────────────────────────────────────────
LEVEL_USER: int = 0       # Basic — no special features
LEVEL_PREMIUM: int = 1    # Premium — AutoReply + AutoBC
LEVEL_SELLER: int = 2     # Seller — can grant Premium
LEVEL_OWNER: int = 3      # Owner — full access

LEVEL_NAMES: dict[int, str] = {
    LEVEL_USER: "User",
    LEVEL_PREMIUM: "Premium ⭐",
    LEVEL_SELLER: "Seller 💼",
    LEVEL_OWNER: "Owner 👑",
}

# ── AutoBC limits ─────────────────────────────────────────────────────────────
AUTOBC_MIN_INTERVAL: int = 30    # seconds — minimum broadcast interval
AUTOBC_MAX_MESSAGES: int = 50    # maximum stored BC messages per user

# ── AutoReply limits ──────────────────────────────────────────────────────────
AUTOREPLY_MAX_TRIGGERS: int = 50  # maximum trigger→response pairs per user
