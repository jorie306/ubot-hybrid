import asyncio
import os

from pyrogram import Client, filters

# =========================================
# VARIABLES
# =========================================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

ACTIVE_UBOT = {}
UBOT_MESSAGE = {}
UBOT_DELAY = {}
AUTO_BC = {}

# =========================================
# LOAD USERBOT
# =========================================

def load_userbot(app):

    # =====================================
    # /on
    # =====================================

    @app.on_message(filters.command("on"))
    async def ubot_on(client, message):

        user_id = message.from_user.id

        ACTIVE_UBOT[user_id] = True

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

        AUTO_BC[user_id] = False

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

        delay = UBOT_DELAY.get(
            user_id,
            300
        )

        text = UBOT_MESSAGE.get(
            user_id,
            "Belum diset"
        )

        autobc = AUTO_BC.get(
            user_id,
            False
        )

        await message.reply_text(
            f"""
📊 USERBOT STATUS

👤 Active:
{status}

📢 Message:
{text}

⏱ Delay:
{delay}

🔁 AutoBC:
{autobc}
"""
        )

    # =====================================
    # /setmsg
    # =====================================

    @app.on_message(filters.command("setmsg"))
    async def setmsg(client, message):

        user_id = message.from_user.id

        if len(message.command) < 2:

            return await message.reply_text(
                "Usage:\n/setmsg halo"
            )

        text = message.text.split(
            None,
            1
        )[1]

        UBOT_MESSAGE[user_id] = text

        await message.reply_text(
            f"""
✅ MESSAGE UPDATED

📢 Message:
{text}
"""
        )

    # =====================================
    # /delay
    # =====================================

    @app.on_message(filters.command("delay"))
    async def delay(client, message):

        user_id = message.from_user.id

        try:

            delay_value = int(
                message.command[1]
            )

            UBOT_DELAY[user_id] = delay_value

            await message.reply_text(
                f"""
✅ DELAY UPDATED

⏱ Delay:
{delay_value} seconds
"""
            )

        except:

            await message.reply_text(
                "❌ Example:\n/delay 300"
            )

    # =====================================
    # /autobcon
    # =====================================

    @app.on_message(filters.command("autobcon"))
    async def autobcon(client, message):

        user_id = message.from_user.id

        if not ACTIVE_UBOT.get(user_id):

            return await message.reply_text(
                "❌ Userbot belum aktif"
            )

        AUTO_BC[user_id] = True

        await message.reply_text(
            """
✅ AUTO BROADCAST ENABLED

🚀 AutoBC started
"""
        )

        # =================================
        # START USER CLIENT
        # =================================

        session_name = f"sessions/{user_id}"

        user = Client(
            session_name,
            api_id=API_ID,
            api_hash=API_HASH
        )

        await user.start()

        while AUTO_BC.get(user_id):

            text = UBOT_MESSAGE.get(
                user_id,
                "TEST"
            )

            delay = UBOT_DELAY.get(
                user_id,
                300
            )

            async for dialog in user.get_dialogs():

                try:

                    chat = dialog.chat

                    if chat.type.name in [
                        "GROUP",
                        "SUPERGROUP"
                    ]:

                        await user.send_message(
                            chat.id,
                            text
                        )

                        await asyncio.sleep(3)

                except:

                    pass

            await asyncio.sleep(delay)

        await user.stop()

    # =====================================
    # /autobcoff
    # =====================================

    @app.on_message(filters.command("autobcoff"))
    async def autobcoff(client, message):

        user_id = message.from_user.id

        AUTO_BC[user_id] = False

        await message.reply_text(
            """
🛑 AUTO BROADCAST DISABLED
"""
        )
