print("USERBOT MODULE LOADED")

from pyrogram import filters

# =========================================
# USERBOT DATA
# =========================================

ACTIVE_UBOT = {}

# =========================================
# LOAD USERBOT
# =========================================

def load_userbot(app):

    print("LOAD USERBOT BERHASIL")

    # =====================================
    # /on
    # =====================================

    @app.on_message(filters.command("on"))
    async def ubot_on(client, message):

        user_id = message.from_user.id

        ACTIVE_UBOT[user_id] = True

        print("COMMAND ON MASUK")

        await message.reply_text(
            """
✅ USERBOT ACTIVE

🚀 Userbot online
"""
        )

    # =====================================
    # /off
    # =====================================

    @app.on_message(filters.command("off"))
    async def ubot_off(client, message):

        user_id = message.from_user.id

        ACTIVE_UBOT[user_id] = False

        print("COMMAND OFF MASUK")

        await message.reply_text(
            "🛑 USERBOT OFFLINE"
        )

    # =====================================
    # /status
    # =====================================

    @app.on_message(filters.command("status"))
    async def ubot_status(client, message):

        user_id = message.from_user.id

        status = ACTIVE_UBOT.get(
            user_id,
            False
        )

        print("COMMAND STATUS MASUK")

        await message.reply_text(
            f"""
📊 USERBOT STATUS

👤 Active:
{status}
"""
        )
