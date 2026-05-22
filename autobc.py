import asyncio

from pyrogram import filters

# =========================================
# SETTINGS
# =========================================

AUTO_BC = False
AUTO_BC_TEXT = "TEST"
AUTO_BC_DELAY = 300

# =========================================
# LOAD AUTOBROADCAST
# =========================================

def load_autobc(app):

    # =====================================
    # SET MESSAGE
    # =====================================

    @app.on_message(filters.command("autobc"))
    async def set_autobc(_, msg):

        global AUTO_BC_TEXT

        if len(msg.command) < 2:

            return await msg.reply(
                "Usage:\n/autobc pesan"
            )

        AUTO_BC_TEXT = msg.text.split(
            None,
            1
        )[1]

        await msg.reply(
            f"""
✅ Auto BC Message Set

📢 Message:
{AUTO_BC_TEXT}
"""
        )

    # =====================================
    # SET DELAY
    # =====================================

    @app.on_message(filters.command("setdelay"))
    async def set_delay(_, msg):

        global AUTO_BC_DELAY

        if len(msg.command) < 2:

            return await msg.reply(
                "Usage:\n/setdelay 300"
            )

        try:

            AUTO_BC_DELAY = int(
                msg.command[1]
            )

            await msg.reply(
                f"""
✅ Delay Updated

⏱ Delay:
{AUTO_BC_DELAY} seconds
"""
            )

        except:

            await msg.reply(
                "❌ Delay harus angka"
            )

    # =====================================
    # AUTO BC ON
    # =====================================

    @app.on_message(filters.command("autobcon"))
    async def autobc_on(_, msg):

        global AUTO_BC

        if AUTO_BC:

            return await msg.reply(
                "⚠️ Auto BC sudah aktif"
            )

        AUTO_BC = True

        await msg.reply(
            "✅ Auto BC Enabled"
        )

        while AUTO_BC:

            async for dialog in app.get_dialogs():

                try:

                    chat = dialog.chat

                    if chat.type.name in [
                        "GROUP",
                        "SUPERGROUP"
                    ]:

                        await app.send_message(
                            chat.id,
                            f"📢 AUTO BC\n\n{AUTO_BC_TEXT}"
                        )

                        await asyncio.sleep(3)

                except:

                    pass

            await asyncio.sleep(
                AUTO_BC_DELAY
            )

    # =====================================
    # AUTO BC OFF
    # =====================================

    @app.on_message(filters.command("autobcoff"))
    async def autobc_off(_, msg):

        global AUTO_BC

        AUTO_BC = False

        await msg.reply(
            "🛑 Auto BC Disabled"
        )
