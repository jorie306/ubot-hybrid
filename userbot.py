from pyrogram import filters

# =========================================
# USERBOT DATA
# =========================================

ACTIVE_UBOT = {}

# =========================================
# LOAD USERBOT
# =========================================

def load_userbot(app):

    # =====================================
    # /on
    # =====================================

    @app.on_message(filters.command("on"))
    async def ubot_on(_, msg):

        user_id = msg.from_user.id

        ACTIVE_UBOT[user_id] = True

        await msg.reply(
            """
✅ USERBOT ACTIVE

🚀 Session detected
👤 Userbot online
"""
        )

    # =====================================
    # /off
    # =====================================

    @app.on_message(filters.command("off"))
    async def ubot_off(_, msg):

        user_id = msg.from_user.id

        ACTIVE_UBOT[user_id] = False

        await msg.reply(
            """
🛑 USERBOT OFFLINE
"""
        )

    # =====================================
    # /status
    # =====================================

    @app.on_message(filters.command("status"))
    async def ubot_status(_, msg):

        user_id = msg.from_user.id

        status = ACTIVE_UBOT.get(
            user_id,
            False
        )

        await msg.reply(
            f"""
📊 USERBOT STATUS

👤 Active:
{status}

✅ Railway Online
✅ Session Ready
"""
        )
