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
    # .on
    # =====================================

    @app.on_message(filters.regex(r"^\.on$"))
    async def ubot_on(_, msg):

        user_id = msg.from_user.id

        UBOT_STATUS[user_id] = True

        await msg.reply(
            "✅ USERBOT ACTIVE"
        )

    # =====================================
    # .off
    # =====================================

    @app.on_message(filters.regex(r"^\.off$"))
    async def ubot_off(_, msg):

        user_id = msg.from_user.id

        UBOT_STATUS[user_id] = False

        await msg.reply(
            "🛑 USERBOT OFF"
        )

    # =====================================
    # .setmsg
    # =====================================

    @app.on_message(filters.regex(r"^\.setmsg"))
    async def set_msg(_, msg):

        user_id = msg.from_user.id

        text = msg.text.replace(
            ".setmsg ",
            ""
        )

        UBOT_MESSAGE[user_id] = text

        await msg.reply(
            f"✅ Message set:\n\n{text}"
        )

    # =====================================
    # .delay
    # =====================================

    @app.on_message(filters.regex(r"^\.delay"))
    async def set_delay(_, msg):

        user_id = msg.from_user.id

        try:

            delay = int(
                msg.text.split()[1]
            )

            UBOT_DELAY[user_id] = delay

            await msg.reply(
                f"✅ Delay set to {delay}s"
            )

        except:

            await msg.reply(
                "❌ Example:\n.delay 300"
            )

    # =====================================
    # .autobc on
    # =====================================

    @app.on_message(filters.regex(r"^\.autobc on$"))
    async def autobc_on(_, msg):

        await msg.reply(
            "✅ AUTOBC ENABLED"
        )

    # =====================================
    # .autobc off
    # =====================================

    @app.on_message(filters.regex(r"^\.autobc off$"))
    async def autobc_off(_, msg):

        await msg.reply(
            "🛑 AUTOBC DISABLED"
        )

    # =====================================
    # .status
    # =====================================

    @app.on_message(filters.regex(r"^\.status$"))
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
    # .ping
    # =====================================

    @app.on_message(filters.regex(r"^\.ping$"))
    async def ping(_, msg):

        await msg.reply(
            "🏓 Pong!"
        )
