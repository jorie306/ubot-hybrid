from pyrogram import filters

# =========================================
# LOAD BROADCAST
# =========================================

def load_broadcast(app):

    # =====================================
    # BROADCAST
    # =====================================

    @app.on_message(filters.command("bc"))
    async def broadcast(_, msg):

        if len(msg.command) < 2:

            return await msg.reply(
                "Usage:\n/bc pesan"
            )

        text = msg.text.split(
            None,
            1
        )[1]

        await msg.reply(
            f"📣 Broadcast:\n\n{text}"
        )
