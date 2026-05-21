import os
import sqlite3
import asyncio

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
# DATABASE
# =========================================

db = sqlite3.connect(
    "storebot.db",
    check_same_thread=False
)

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")

db.commit()

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

    user_id = msg.from_user.id

    cursor.execute(
        "INSERT OR IGNORE INTO users(user_id) VALUES(?)",
        (user_id,)
    )

    db.commit()

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
# BROADCAST
# =========================================

@app.on_message(filters.command("bc"))
async def broadcast(_, msg):

    if len(msg.command) < 2:

        return await msg.reply(
            "Usage:\n/bc pesan"
        )

    text = msg.text.split(
        None,
        1
    )[1]

    cursor.execute(
        "SELECT user_id FROM users"
    )

    users = cursor.fetchall()

    success = 0
    failed = 0

    status = await msg.reply(
        "📣 Broadcasting..."
    )

    for user in users:

        user_id = user[0]

        try:

            await app.send_message(
                user_id,
                f"📢 BROADCAST\n\n{text}"
            )

            success += 1

            await asyncio.sleep(1)

        except:

            failed += 1

    await status.edit_text(
        f"""
✅ Broadcast selesai

✔ Success : {success}
❌ Failed : {failed}
"""
    )

# =========================================
# CALLBACK BUTTON
# =========================================

@app.on_callback_query()
async def callback(_, query):

    data = query.data

    if data == "premium":

        await query.message.reply(
            """
👑 PREMIUM ACCESS

Hubungi owner untuk membeli akses premium.
"""
        )

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
