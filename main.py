import os

from pyrogram import (
    Client,
    filters
)

from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

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
    bot_token=BOT_TOKEN,
    workers=100
)

# =========================================
# IMPORT MODULES
# =========================================

from modules import panel

# =========================================
# START BUTTON
# =========================================

START_BUTTON = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "👑 Premium",
                callback_data="premium"
            ),
            InlineKeyboardButton(
                "🛒 Buy",
                callback_data="buy"
            )
        ]
    ]
)

# =========================================
# START COMMAND
# =========================================

@app.on_message(filters.command("start"))
async def start(_, msg):

    text = """
🤖 STOREBOT ACTIVE

✅ Bot Online
✅ Railway Connected
"""

    await msg.reply(
        text,
        reply_markup=START_BUTTON
    )

# =========================================
# HELP COMMAND
# =========================================

@app.on_message(filters.command("help"))
async def help_cmd(_, msg):

    text = """
📌 STOREBOT MENU

AVAILABLE:
• /panel
• /help
"""

    await msg.reply(text)

# =========================================
# CALLBACK BUTTON
# =========================================

@app.on_callback_query()
async def callback(_, query):

    data = query.data

    if data == "premium":

        await query.message.reply(
            "👑 Premium menu active"
        )

    elif data == "buy":

        await query.message.reply(
            "🛒 Hubungi owner untuk membeli premium"
        )

# =========================================
# ONLINE
# =========================================

print("🚀 STOREBOT ONLINE")

app.run()
