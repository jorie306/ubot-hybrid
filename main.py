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
from broadcast import load_broadcast

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
# LOAD MODULES
# =========================================

load_panel(app)
load_broadcast(app)

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
        ],
        [
            InlineKeyboardButton(
                "📣 Channel",
                url="https://t.me/usernamechannel"
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
✅ Broadcast Ready
✅ Panel Ready
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

AVAILABLE COMMANDS:

• /start
• /help
• /panel
• /bc

👑 OWNER:
• /addadmin
• /addseller
• /addprem

📣 BROADCAST:
• /bc pesan
"""

    await msg.reply(text)

# =========================================
# CALLBACK BUTTON
# =========================================

@app.on_callback_query()
async def callback(_, query):

    data = query.data

    # PREMIUM
    if data == "premium":

        await query.message.reply(
            """
👑 PREMIUM ACCESS

Hubungi owner untuk membeli akses premium.
"""
        )

    # BUY
    elif data == "buy":

        await query.message.reply(
            """
🛒 PEMBELIAN PREMIUM

Silahkan hubungi owner/admin.
"""
        )

# =========================================
# ONLINE
# =========================================

print("🚀 STOREBOT ONLINE")

app.run()
