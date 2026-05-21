from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from database import (
    get_role,
    set_role,
    has_access
)

# =========================================
# PANEL BUTTON
# =========================================

OWNER_PANEL = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "👑 Add Admin",
                callback_data="add_admin"
            )
        ]
    ]
)

# =========================================
# LOAD APP
# =========================================

def load_panel(app):

    # =====================================
    # PANEL
    # =====================================

    @app.on_message(filters.command("panel"))
    async def panel_cmd(_, msg):

        role = get_role(msg.from_user.id)

        if role != "OWNER":

            return await msg.reply(
                "❌ Kamu bukan owner"
            )

        await msg.reply(
            "👑 OWNER PANEL ACTIVE",
            reply_markup=OWNER_PANEL
        )

    # =====================================
    # ADD ADMIN
    # =====================================

    @app.on_message(filters.command("addadmin"))
    async def add_admin(_, msg):

        if get_role(msg.from_user.id) != "OWNER":

            return await msg.reply(
                "❌ Owner only"
            )

        if len(msg.command) < 2:

            return await msg.reply(
                "Usage:\n/addadmin user_id"
            )

        target = int(msg.command[1])

        set_role(target, "ADMIN")

        await msg.reply(
            f"✅ {target} sekarang ADMIN"
        )
