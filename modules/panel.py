from pyrogram import filters, Client
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# =========================================
# APP
# =========================================

app = Client.get_instance()

# =========================================
# DATABASE IMPORT
# =========================================

from database import (
    get_role,
    set_role,
    has_access
)

# =========================================
# OWNER PANEL
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
            ),
            InlineKeyboardButton(
                "📣 Broadcast",
                callback_data="broadcast"
            )
        ],
        [
            InlineKeyboardButton(
                "📊 Statistics",
                callback_data="stats"
            )
        ]
    ]
)

# =========================================
# ADMIN PANEL
# =========================================

ADMIN_PANEL = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "🛒 Add Seller",
                callback_data="admin_addseller"
            ),
            InlineKeyboardButton(
                "💎 Add Premium",
                callback_data="admin_addprem"
            )
        ]
    ]
)

# =========================================
# SELLER PANEL
# =========================================

SELLER_PANEL = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "💎 Add Premium",
                callback_data="seller_addprem"
            )
        ]
    ]
)

# =========================================
# PANEL COMMAND
# =========================================

@app.on_message(filters.command("panel"))
async def panel_menu(_, msg):

    user_id = msg.from_user.id
    role = get_role(user_id)

    # OWNER
    if role == "OWNER":

        return await msg.reply(
            """
👑 OWNER PANEL

✅ Full Access Enabled
""",
            reply_markup=OWNER_PANEL
        )

    # ADMIN
    elif role == "ADMIN":

        return await msg.reply(
            """
🛠 ADMIN PANEL

✅ Admin Access Enabled
""",
            reply_markup=ADMIN_PANEL
        )

    # SELLER
    elif role == "SELLER":

        return await msg.reply(
            """
🛒 SELLER PANEL

✅ Seller Access Enabled
""",
            reply_markup=SELLER_PANEL
        )

    # FREE / PREM
    else:

        return await msg.reply(
            "❌ Kamu tidak memiliki akses panel"
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
# DELETE ADMIN
# =========================================

@app.on_message(filters.command("deladmin"))
async def del_admin(_, msg):

    if get_role(msg.from_user.id) != "OWNER":
        return await msg.reply(
            "❌ Owner only"
        )

    if len(msg.command) < 2:
        return await msg.reply(
            "Usage:\n/deladmin user_id"
        )

    target = int(msg.command[1])

    set_role(target, "FREE")

    await msg.reply(
        f"✅ {target} dihapus dari ADMIN"
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
# DELETE SELLER
# =========================================

@app.on_message(filters.command("delseller"))
async def del_seller(_, msg):

    if not has_access(msg.from_user.id, "ADMIN"):
        return await msg.reply(
            "❌ Admin access required"
        )

    if len(msg.command) < 2:
        return await msg.reply(
            "Usage:\n/delseller user_id"
        )

    target = int(msg.command[1])

    set_role(target, "FREE")

    await msg.reply(
        f"✅ {target} dihapus dari SELLER"
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
# DELETE PREMIUM
# =========================================

@app.on_message(filters.command("delprem"))
async def del_prem(_, msg):

    if not has_access(msg.from_user.id, "SELLER"):
        return await msg.reply(
            "❌ Seller access required"
        )

    if len(msg.command) < 2:
        return await msg.reply(
            "Usage:\n/delprem user_id"
        )

    target = int(msg.command[1])

    set_role(target, "FREE")

    await msg.reply(
        f"✅ {target} premium dihapus"
    )

# =========================================
# CALLBACK BUTTONS
# =========================================

@app.on_callback_query()
async def callback_handler(_, query):

    data = query.data
    role = get_role(query.from_user.id)

    # OWNER CALLBACK
    if role == "OWNER":

        if data == "add_admin":

            return await query.message.reply(
                """
👑 ADD ADMIN

Gunakan:
/addadmin user_id
"""
            )

        elif data == "add_seller":

            return await query.message.reply(
                """
🛒 ADD SELLER

Gunakan:
/addseller user_id
"""
            )

        elif data == "add_prem":

            return await query.message.reply(
                """
💎 ADD PREMIUM

Gunakan:
/addprem user_id
"""
            )

        elif data == "broadcast":

            return await query.message.reply(
                """
📣 BROADCAST

Gunakan:
/bc pesan
"""
            )

        elif data == "stats":

            return await query.message.reply(
                """
📊 BOT STATISTICS

✅ System Online
✅ Panel Active
"""
            )

    # ADMIN CALLBACK
    elif role == "ADMIN":

        if data == "admin_addseller":

            return await query.message.reply(
                """
🛒 ADD SELLER

Gunakan:
/addseller user_id
"""
            )

        elif data == "admin_addprem":

            return await query.message.reply(
                """
💎 ADD PREMIUM

Gunakan:
/addprem user_id
"""
            )

    # SELLER CALLBACK
    elif role == "SELLER":

        if data == "seller_addprem":

            return await query.message.reply(
                """
💎 ADD PREMIUM

Gunakan:
/addprem user_id
"""
            )

# =========================================
# ROLE HELP
# =========================================

@app.on_message(filters.command("rolehelp"))
async def role_help(_, msg):

    role = get_role(msg.from_user.id)

    text = f"""
👤 ROLE: {role}

📌 COMMAND LIST
"""

    if role == "OWNER":

        text += """

👑 OWNER COMMANDS
• /panel
• /addadmin
• /deladmin
• /addseller
• /delseller
• /addprem
• /delprem
• /bc
• /gcast
"""

    elif role == "ADMIN":

        text += """

🛠 ADMIN COMMANDS
• /panel
• /addseller
• /delseller
• /addprem
• /delprem
"""

    elif role == "SELLER":

        text += """

🛒 SELLER COMMANDS
• /panel
• /addprem
• /delprem
"""

    elif role == "PREM":

        text += """

💎 PREMIUM COMMANDS
• /help
• /afk
"""

    else:

        text += """

❌ FREE USER
"""

    await msg.reply(text)
