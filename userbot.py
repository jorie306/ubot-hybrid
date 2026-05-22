from pyrogram import filters

# =========================================
# SETTINGS
# =========================================

UBOT_STATUS = {}
UBOT_MESSAGE = {}
UBOT_DELAY = {}

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

        UBOT_STATUS[user_id] = True

        await msg.reply(
            "✅ USERBOT ACTIVE"
        )

    # =====================================
    # /off
    # =====================================

    @app.on_message(filters.command("off"))
    async def ubot_off(_, msg):

        user_id = msg.from_user.id

        UBOT_STATUS[user_id] = False

        await msg.reply(
            "🛑 USERBOT OFF"
        )

    # =====================================
    # /setmsg
    # =====================================

    @app.on_message(filters.command("setmsg"))
    async def set_msg(_, msg):

        user_id = msg.from_user.id

        if len(msg.command) < 2:

            return await msg.reply(
                "Usage:\n/setmsg halo"
            )

        text = msg.text.split(
            None,
            1
        )[1]

        UBOT_MESSAGE[user_id] = text

        await msg.reply(
            f"✅ Message updated\n\n{text}"
        )

    # =====================================
    # /delay
    # =====================================

    @app.on_message(filters.command("delay"))
    async def set_delay(_, msg):

        user_id = msg.from_user.id

        try:

            delay = int(msg.command[1])

            UBOT_DELAY[user_id] = delay

            await msg.reply(
                f"✅ Delay set to {delay}s"
            )

        except:

            await msg.reply(
                "❌ Example:\n/delay 300"
            )

    # =====================================
    # /autobcon
    # =====================================

    @app.on_message(filters.command("autobcon"))
    async def autobc_on(_, msg):

        await msg.reply(
            "✅ AUTOBC ENABLED"
        )

    # =====================================
    # /autobcoff
    # =====================================

    @app.on_message(filters.command("autobcoff"))
    async def autobc_off(_, msg):

        await msg.reply(
            "🛑 AUTOBC DISABLED"
        )

    # =====================================
    # /status
    # =====================================

    @app.on_message(filters.command("status"))
    async def status(_, msg):

        user_id = msg.from_user.id

        status = UBOT_STATUS.get(
            user_id,
            False
        )

        text = UBOT_MESSAGE.get(
            user_id,
            "Belum diset"
        )

        delay = UBOT_DELAY.get(
            user_id,
            300
        )

        await msg.reply(
            f"""
📊 USERBOT STATUS

👤 Active:
{status}

📢 Message:
{text}

⏱ Delay:
{delay}
"""
        )

    # =====================================
    # /ping
    # =====================================

    @app.on_message(filters.command("ping"))
    async def ping(_, msg):

        await msg.reply(
            "🏓 Pong!"
        )
