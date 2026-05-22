import os

from pyrogram import Client, filters

from login import load_login

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client(
    "StoreBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# =========================================
# LOAD LOGIN
# =========================================

load_login(app)

# =========================================
# START
# =========================================

@app.on_message(filters.command("start"))
async def start(client, message):

    await message.reply_text(
        """
🤖 STOREBOT ACTIVE

/login = login userbot
/ping = test bot
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

print("🚀 BOT ONLINE")

app.run()
