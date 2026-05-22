import os

from pyrogram import Client, filters

from login import load_login
from userbot import load_userbot

# =========================================
# VARIABLES
# =========================================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# =========================================
# CLIENT
# =========================================

app = Client(
    "StoreBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# =========================================
# LOAD MODULES
# =========================================

load_login(app)
load_userbot(app)

# =========================================
# START
# =========================================

@app.on_message(filters.command("start"))
async def start(client, message):

    await message.reply_text(
        """
🤖 STOREBOT ACTIVE

📌 COMMAND:

GENERAL:
• /start
• /ping

LOGIN:
• /login

USERBOT:
• /on
• /off
• /status
"""
    )

# =========================================
# PING
# =========================================

@app.on_message(filters.command("ping"))
async def ping(client, message):

    await message.reply_text(
        "🏓 PONG"
    )

# =========================================
# ONLINE
# =========================================

print("🚀 BOT ONLINE")

app.run()
