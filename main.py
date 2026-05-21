import os

from pyrogram import (
    Client,
    filters
)

from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from panel import load_panel

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
# LOAD PANEL
# =========================================

load_panel(app)

# =========================================
# START BUTTON
# =========================================

START_BUTTON = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "👑 Premium",
                callback_data="premium"
            )
        ]
    ]
)

# =========================================
# START
# =========================================

@app.on_message(filters.command("start"))
async def start(_, msg):

    await msg.reply(
        "✅ STOREBOT ONLINE",
        reply_markup=START_BUTTON
    )

# =========================================
# HELP
# =========================================

@app.on_message(filters.command("help"))
async def help_cmd(_, msg):

    await msg.reply(
        """
📌 COMMANDS

/start
/help
/panel
"""
    )

# =========================================
# ONLINE
# =========================================

print("🚀 STOREBOT ONLINE")

app.run()
