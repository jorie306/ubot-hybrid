import asyncio
import sqlite3

from pyrogram import filters
from database import get_role

# =========================================
# DATABASE
# =========================================

db = sqlite3.connect(
    "storebot.db",
    check_same_thread=False
)

cursor = db.cursor()

# =========================================
# SAVE USER
# =========================================

def save_user(user_id):

    cursor.execute(
        "INSERT OR IGNORE INTO users(user_id) VALUES(?)",
        (user_id,)
    )

    db.commit()

# =========================================
# LOAD BROADCAST
# =========================================

def load_broadcast(app):

    # =====================================
    # AUTO SAVE USER
    # =====================================

    @app.on_message(filters.private)
    async def auto_save(_, msg):

        save_user(msg.from_user.id)

    # =====================================
    # BROADCAST
    # =====================================

    @app.on_message(filters.command("bc"))
    async def broadcast(_, msg):

        role = get_role(msg.from_user.id)

        if role not in ["OWNER", "ADMIN"]:

            return await msg.reply(
                "❌ Access denied"
            )

        if len(msg.command) < 2:

            return await msg.reply(
                "Usage:\n/bc message"
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

                await asyncio.sleep(1.5)

            except:

                failed += 1

        await status.edit_text(
            f"""
✅ Broadcast selesai

✔ Success : {success}
❌ Failed : {failed}
"""
        )
