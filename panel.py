print("USERBOT FILE TERBACA")

from pyrogram import filters

# =========================================
# LOAD USERBOT
# =========================================

def load_userbot(app):

    print("LOAD USERBOT FUNCTION JALAN")

    # =====================================
    # /ping
    # =====================================

    @app.on_message(filters.command("ping"))
    async def ping(client, message):

        print("COMMAND /ping MASUK")

        await message.reply_text(
            "🏓 PONG BERHASIL"
        )

    # =====================================
    # /on
    # =====================================

    @app.on_message(filters.command("on"))
    async def on_cmd(client, message):

        print("COMMAND /on MASUK")

        await message.reply_text(
            "✅ USERBOT ACTIVE"
        )

    # =====================================
    # /off
    # =====================================

    @app.on_message(filters.command("off"))
    async def off_cmd(client, message):

        print("COMMAND /off MASUK")

        await message.reply_text(
            "🛑 USERBOT OFF"
        )

    # =====================================
    # /status
    # =====================================

    @app.on_message(filters.command("status"))
    async def status_cmd(client, message):

        print("COMMAND /status MASUK")

        await message.reply_text(
            """
📊 USERBOT STATUS

✅ Module Loaded
✅ Commands Working
✅ Railway Active
"""
        )
