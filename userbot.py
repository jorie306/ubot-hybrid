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
    # UBOT ON
    # =====================================

    @app.on_message(filters.command("on", prefixes="."))
    async def ubot_on(_, msg):

        user_id = msg.from_user.id

        UBOT_STATUS[user_id] = True

        await msg.reply(
            """
✅ USERBOT ACTIVE

🚀 Userbot berhasil diaktifkan
"""
        )

    # =====================================
    # UBOT OFF
    # =====================================

    @app.on_message(filters.command("off", prefixes="."))
    async def ubot_off(_, msg):

        user_id = msg.from_user.id

        UBOT_STATUS[user_id] = False

        await msg.reply(
            """
🛑 USERBOT OFFLINE
"""
        )

    # =====================================
    # SET MESSAGE
    # =====================================

    @app.on_message(filters.command("setmsg", prefixes="."))
    async def set_msg(_, msg):

        user_id = msg.from_user.id

        if len(msg.command) < 2:

            return await msg.reply(
                "Usage:\n.setmsg pesan"
            )

        text = msg.text.split(
            None,
            1
        )[1]

        UBOT_MESSAGE[user_id] = text

        await msg.reply(
            f"""
✅ MESSAGE UPDATED

📢 Message:
{text}
"""
        )

    # =====================================
    # SET DELAY
    # =====================================

    @app.on_message(filters.command("delay", prefixes="."))
    async def set_delay(_, msg):

        user_id = msg.from_user.id

        if len(msg.command) < 2:

            return await msg.reply(
                "Usage:\n.delay 300"
            )

        try:

            delay = int(msg.command[1])

            UBOT_DELAY[user_id] = delay

            await msg.reply(
                f"""
✅ DELAY UPDATED

⏱ Delay:
{delay} seconds
"""
            )

        except:

            await msg.reply(
                "❌ Delay harus angka"
            )

    # =====================================
    # AUTOBC ON
    # =====================================

    @app.on_message(filters.regex(r"^\.autobc on$"))
    async def autobc_on(_, msg):

        await msg.reply(
            """
✅ AUTOBC ENABLED

📢 Auto broadcast started
"""
        )

    # =====================================
    # AUTOBC OFF
    # =====================================

    @app.on_message(filters.regex(r"^\.autobc off$"))
    async def autobc_off(_, msg):

        await msg.reply(
            """
🛑 AUTOBC DISABLED
"""
        )

    # =====================================
    # STATUS
    # =====================================

    @app.on_message(filters.command("status", prefixes="."))
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
    # PING
    # =====================================

    @app.on_message(filters.command("ping", prefixes="."))
    async def ping(_, msg):

        await msg.reply(
            "🏓 Pong!"
        )
