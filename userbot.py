import os
import asyncio

from pyrogram import Client, filters

# =========================================
# SETTINGS
# =========================================

UBOT = {}

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# =========================================
# START USERBOT
# =========================================

async def start_userbot(user_id):

    session_name = f"sessions/{user_id}"

    app = Client(
        session_name,
        api_id=API_ID,
        api_hash=API_HASH
    )

    await app.start()

    UBOT[user_id] = {
        "client": app,
        "autobc": False,
        "text": "TEST",
        "delay": 300
    }

    return app

# =========================================
# LOAD USERBOT
# =========================================

def load_userbot(bot):

    # =====================================
    # UBOT ON
    # =====================================

    @bot.on_message(filters.command("uboton"))
    async def ubot_on(_, msg):

        user_id = msg.from_user.id

        try:

            app = await start_userbot(
                user_id
            )

            me = await app.get_me()

            await msg.reply(
                f"""
✅ USERBOT ACTIVE

👤 Account:
{me.first_name}
"""
            )

        except Exception as e:

            await msg.reply(
                f"❌ Error:\n{e}"
            )

    # =====================================
    # SET MESSAGE
    # =====================================

    @bot.on_message(filters.command("setubotmsg"))
    async def set_msg(_, msg):

        user_id = msg.from_user.id

        if user_id not in UBOT:

            return await msg.reply(
                "❌ Userbot belum aktif"
            )

        if len(msg.command) < 2:

            return await msg.reply(
                "Usage:\n/setubotmsg pesan"
            )

        text = msg.text.split(
            None,
            1
        )[1]

        UBOT[user_id]["text"] = text

        await msg.reply(
            "✅ Message updated"
        )

    # =====================================
    # SET DELAY
    # =====================================

    @bot.on_message(filters.command("setubotdelay"))
    async def set_delay(_, msg):

        user_id = msg.from_user.id

        if user_id not in UBOT:

            return await msg.reply(
                "❌ Userbot belum aktif"
            )

        if len(msg.command) < 2:

            return await msg.reply(
                "Usage:\n/setubotdelay 300"
            )

        try:

            delay = int(
                msg.command[1]
            )

            UBOT[user_id]["delay"] = delay

            await msg.reply(
                f"✅ Delay set to {delay}s"
            )

        except:

            await msg.reply(
                "❌ Delay harus angka"
            )

    # =====================================
    # AUTOBC ON
    # =====================================

    @bot.on_message(filters.command("ubotautobcon"))
    async def autobc_on(_, msg):

        user_id = msg.from_user.id

        if user_id not in UBOT:

            return await msg.reply(
                "❌ Userbot belum aktif"
            )

        ubot = UBOT[user_id]

        if ubot["autobc"]:

            return await msg.reply(
                "⚠️ AutoBC sudah aktif"
            )

        ubot["autobc"] = True

        await msg.reply(
            "✅ Userbot AutoBC Enabled"
        )

        app = ubot["client"]

        while ubot["autobc"]:

            async for dialog in app.get_dialogs():

                try:

                    chat = dialog.chat

                    if chat.type.name in [
                        "GROUP",
                        "SUPERGROUP"
                    ]:

                        await app.send_message(
                            chat.id,
                            ubot["text"]
                        )

                        await asyncio.sleep(3)

                except:

                    pass

            await asyncio.sleep(
                ubot["delay"]
            )

    # =====================================
    # AUTOBC OFF
    # =====================================

    @bot.on_message(filters.command("ubotautobcoff"))
    async def autobc_off(_, msg):

        user_id = msg.from_user.id

        if user_id not in UBOT:

            return await msg.reply(
                "❌ Userbot belum aktif"
            )

        UBOT[user_id]["autobc"] = False

        await msg.reply(
            "🛑 Userbot AutoBC Disabled"
        )
