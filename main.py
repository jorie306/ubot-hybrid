# =========================
# FILE: main.py
# =========================

import os
import asyncio
import sqlite3
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# =========================
# CONFIG
# =========================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = int(os.getenv("OWNER_ID"))

# =========================
# CLIENT
# =========================

app = Client(
    "StoreBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=100,
    in_memory=False
)

# =========================
# DATABASE
# =========================

db = sqlite3.connect("storebot.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    role TEXT DEFAULT 'FREE'
)
""")

db.commit()

# =========================
# ROLE SYSTEM
# =========================

ROLES = {
    "OWNER": 4,
    "ADMIN": 3,
    "SELLER": 2,
    "PREM": 1,
    "FREE": 0
}

def get_role(user_id):
    cursor.execute(
        "SELECT role FROM users WHERE user_id=?",
        (user_id,)
    )
    data = cursor.fetchone()

    if data:
        return data[0]

    return "FREE"

def set_role(user_id, role):
    cursor.execute(
        "INSERT OR REPLACE INTO users(user_id, role) VALUES(?, ?)",
        (user_id, role)
    )
    db.commit()

def has_access(user_id, role):
    return ROLES.get(get_role(user_id), 0) >= ROLES.get(role, 0)

# =========================
# BUTTON MENU
# =========================

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
                url="https://t.me/channelkamu"
            )
        ]
    ]
)

# =========================
# AUTO BC
# =========================

bc_running = False

async def start_bc(text, delay):
    global bc_running
    bc_running = True

    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    while bc_running:
        for user in users:
            try:
                await app.send_message(
                    user[0],
                    text
                )
                await asyncio.sleep(delay)
            except:
                pass

        break

def stop_bc():
    global bc_running
    bc_running = False

# =========================
# GCAST
# =========================

async def gcast(text, delay):
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    for user in users:
        try:
            await app.send_message(
                user[0],
                text
            )
            await asyncio.sleep(delay)
        except:
            pass

# =========================
# AFK
# =========================

AFK = {}

# =========================
# START
# =========================

@app.on_message(filters.command("start"))
async def start(_, msg):

    user_id = msg.from_user.id

    cursor.execute(
        "INSERT OR IGNORE INTO users(user_id) VALUES(?)",
        (user_id,)
    )

    db.commit()

    role = get_role(user_id)

    text = f"""
🤖 Welcome To StoreBot

👤 ID: {user_id}
🎖 Role: {role}

✅ Bot Online
"""

    await msg.reply(
        text,
        reply_markup=START_BUTTON
    )

# =========================
# HELP
# =========================

@app.on_message(filters.command("help"))
async def help_cmd(_, msg):

    role = get_role(msg.from_user.id)

    text = f"""
📌 STOREBOT MENU

👤 Role: {role}

FEATURES:
• Autobc
• Auto Forward
• Gcast
• AFK
• Plugin Custom
• Premium Access
"""

    if role == "OWNER":
        text += """

👑 OWNER MENU
/addadmin
/deladmin
/addseller
/addprem
/bc
/gcast
"""

    elif role == "ADMIN":
        text += """

🛠 ADMIN MENU
/addseller
/addprem
"""

    elif role == "SELLER":
        text += """

🛒 SELLER MENU
/addprem
"""

    await msg.reply(text)

# =========================
# ADD ADMIN
# =========================

@app.on_message(filters.command("addadmin"))
async def add_admin(_, msg):

    if msg.from_user.id != OWNER_ID:
        return

    if len(msg.command) < 2:
        return await msg.reply(
            "Usage:\n/addadmin user_id"
        )

    target = int(msg.command[1])

    set_role(target, "ADMIN")

    await msg.reply(
        f"✅ {target} sekarang ADMIN"
    )

# =========================
# ADD SELLER
# =========================

@app.on_message(filters.command("addseller"))
async def add_seller(_, msg):

    if not has_access(msg.from_user.id, "ADMIN"):
        return

    if len(msg.command) < 2:
        return await msg.reply(
            "Usage:\n/addseller user_id"
        )

    target = int(msg.command[1])

    set_role(target, "SELLER")

    await msg.reply(
        f"✅ {target} sekarang SELLER"
    )

# =========================
# ADD PREMIUM
# =========================

@app.on_message(filters.command("addprem"))
async def add_prem(_, msg):

    if not has_access(msg.from_user.id, "SELLER"):
        return

    if len(msg.command) < 2:
        return await msg.reply(
            "Usage:\n/addprem user_id"
        )

    target = int(msg.command[1])

    set_role(target, "PREM")

    await msg.reply(
        f"✅ {target} sekarang PREMIUM"
    )

# =========================
# BC
# =========================

@app.on_message(filters.command("bc"))
async def bc(_, msg):

    if msg.from_user.id != OWNER_ID:
        return

    text = msg.text.split(None, 1)

    if len(text) < 2:
        return await msg.reply(
            "Usage:\n/bc pesan"
        )

    asyncio.create_task(
        start_bc(
            text[1],
            15
        )
    )

    await msg.reply(
        "✅ Broadcast dimulai"
    )

# =========================
# STOP BC
# =========================

@app.on_message(filters.command("stopbc"))
async def stopbc(_, msg):

    if msg.from_user.id != OWNER_ID:
        return

    stop_bc()

    await msg.reply(
        "🛑 Broadcast dihentikan"
    )

# =========================
# GCAST
# =========================

@app.on_message(filters.command("gcast"))
async def gcast_cmd(_, msg):

    if msg.from_user.id != OWNER_ID:
        return

    text = msg.text.split(None, 1)

    if len(text) < 2:
        return await msg.reply(
            "Usage:\n/gcast pesan"
        )

    asyncio.create_task(
        gcast(
            text[1],
            20
        )
    )

    await msg.reply(
        "✅ Gcast dimulai"
    )

# =========================
# AFK
# =========================

@app.on_message(filters.command("afk"))
async def afk(_, msg):

    reason = "AFK"

    if len(msg.command) > 1:
        reason = msg.text.split(None, 1)[1]

    AFK[msg.from_user.id] = reason

    await msg.reply(
        f"😴 AFK diaktifkan\nReason: {reason}"
    )

# =========================
# AFK CHECK
# =========================

@app.on_message(filters.private)
async def afk_check(_, msg):

    if msg.reply_to_message:

        user = msg.reply_to_message.from_user

        if user.id in AFK:

            await msg.reply(
                f"😴 User sedang AFK\nReason: {AFK[user.id]}"
            )

# =========================
# CALLBACK BUTTON
# =========================

@app.on_callback_query()
async def callback(_, query):

    data = query.data

    if data == "premium":
        await query.message.reply(
            "👑 Premium access tersedia"
        )

    elif data == "buy":
        await query.message.reply(
            "🛒 Hubungi owner untuk membeli premium"
        )

# =========================
# RUN
# =========================

print("🚀 StoreBot Online")

app.run()
