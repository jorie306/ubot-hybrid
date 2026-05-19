"""
bot.py — Entry point for Ubot.

Starts the Telethon bot client, initialises the SQLite database,
registers all event handlers, restores any active AutoBC tasks,
then runs until disconnected.
"""

import asyncio
import logging
import sys

from telethon import TelegramClient

import database as db
from config import API_HASH, API_ID, BOT_TOKEN, OWNER_ID
from handlers import register_handlers, restore_autobc_tasks

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ── Startup validation ────────────────────────────────────────────────────────

def _validate_config() -> None:
    missing = []
    if not API_ID:
        missing.append("API_ID")
    if not API_HASH:
        missing.append("API_HASH")
    if not BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not OWNER_ID:
        missing.append("OWNER_ID")

    if missing:
        logger.critical(
            "Missing required environment variables: %s", ", ".join(missing)
        )
        sys.exit(1)


# ── Main ──────────────────────────────────────────────────────────────────────

async def main() -> None:
    _validate_config()

    logger.info("Initialising database…")
    await db.init_db()

    logger.info("Starting bot (owner_id=%s)…", OWNER_ID)
    bot = TelegramClient("bot_session", API_ID, API_HASH)
    await bot.start(bot_token=BOT_TOKEN)

    me = await bot.get_me()
    logger.info("Bot started: @%s (id=%s)", me.username, me.id)

    register_handlers(bot)
    await restore_autobc_tasks(bot)

    logger.info("🤖 Ubot is running. Press Ctrl+C to stop.")
    await bot.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Ubot stopped by user.")
