from pyrogram import (
    filters,
    Client
)

from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

app = Client.get_instance()

from modules.database import (
    get_role,
    set_role,
    has_access
)

# =========================================
# BUTTON PANEL
# =========================================

OWNER_PANEL = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "👑 Add Admin",
                callback_data="add_admin"
            ),
            InlineKeyboardButton(
                "🛒 Add Seller",
                callback_data="add_seller"
            )
        ],
        [
            InlineKeyboardButton(
                "💎 Add Premium",
                callback_data="add_prem"
            )
        ]
    ]
)

# =========================================
# PANEL COMMAND
# =========================================

@app.on_message(filters.command("panel"))
async def panel_cmd(_, msg):

    role = get_role(msg.from_user.id)

    if role == "OWNER":

        return await msg.reply(
            "👑 OWNER PANEL ACTIVE",
            reply_markup=OWNER_PANEL
        )

    elif role == "ADMIN":

        return await msg.reply(
            "🛠 ADMIN PANEL ACTIVE"
        )

    elif role == "SELLER":

        return await msg.reply(
            "🛒 SELLER PANEL ACTIVE"
        )

    else:

        return await msg.reply(
            "❌ Kamu tidak memiliki akses"
        )

# =========================================
# ADD ADMIN
# =========================================

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

# =========================================
# ADD SELLER
# =========================================

@app.on_message(filters.command("addseller"))
async def add_seller(_, msg):

    if not has_access(msg.from_user.id, "ADMIN"):

        return await msg.reply(
            "❌ Admin access required"
        )

    if len(msg.command) < 2:

        return await msg.reply(
            "Usage:\n/addseller user_id"
        )

    target = int(msg.command[1])

    set_role(target, "SELLER")

    await msg.reply(
        f"✅ {target} sekarang SELLER"
    )

# =========================================
# ADD PREMIUM
# =========================================

@app.on_message(filters.command("addprem"))
async def add_prem(_, msg):

    if not has_access(msg.from_user.id, "SELLER"):

        return await msg.reply(
            "❌ Seller access required"
        )

    if len(msg.command) < 2:

        return await msg.reply(
            "Usage:\n/addprem user_id"
        )

    target = int(msg.command[1])

    set_role(target, "PREM")

    await msg.reply(
        f"✅ {target} sekarang PREMIUM"
    )

# =========================================
# CALLBACK BUTTONS
# =========================================

@app.on_callback_query()
async def callback_handler(_, query):

    data = query.data

    if data == "add_admin":

        await query.message.reply(
            "Gunakan:\n/addadmin user_id"
        )

    elif data == "add_seller":

        await query.message.reply(
            "Gunakan:\n/addseller user_id"
        )

    elif data == "add_prem":

        await query.message.reply(
            "Gunakan:\n/addprem user_id"
        )
