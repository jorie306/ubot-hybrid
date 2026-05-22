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
from autobc import load_autobc
from login import load_login

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

# USERS
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")

# GROUPS
cursor.execute("""
CREATE TABLE IF NOT EXISTS groups (
    chat_id INTEGER PRIMARY KEY
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
# LOAD MODULES
# =========================================

load_panel(app)
load_autobc(app)
load_login(app)

# =========================================
# BUTTONS
# =========================================

START_BUTTON = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "👑 Premium",
                callback_data="premium"
            ),
            InlineKeyboardButton(
                "🚀 Login Userbot",
                callback_data="login"
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
# START
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
✅ Auto BC Ready
✅ Userbot Login Ready
✅ Panel Ready
"""

    await msg.reply(
        text,
        reply_markup=START_BUTTON
    )

# =========================================
# SAVE GROUP
# =========================================

@app.on_message(filters.group)
async def save_group(_, msg):

    chat_id = msg.chat.id

    cursor.execute(
        "INSERT OR IGNORE INTO groups(chat_id) VALUES(?)",
        (chat_id,)
    )

    db.commit()

# =========================================
# HELP
# =========================================

@app.on_message(filters.command("help"))
async def help_cmd(_, msg):

    text = """
📌 STOREBOT MENU

GENERAL:
• /start
• /help
• /login

PANEL:
• /panel
• /addadmin

BROADCAST:
• /bc pesan

AUTO BC:
• /autobc pesan
• /setdelay 300
• /autobcon
• /autobcoff
"""

    await msg.reply(text)

# =========================================
# BROADCAST USER
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
# CALLBACK
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

    # LOGIN
    elif data == "login":

        await query.message.reply(
            """
🚀 LOGIN USERBOT

Ketik:
/login
"""
        )

# =========================================
# ONLINE
# =========================================

print("🚀 STOREBOT ONLINE")

app.run()
