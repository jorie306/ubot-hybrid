# =========================================
# OWNER / ADMIN / SELLER / PREM PANEL
# MODULE SYSTEM
# =========================================

from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from main import app
from database import (
    get_role,
    set_role,
    has_access
)

# =========================================
# OWNER PANEL BUTTON
# =========================================

OWNER_PANEL = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "👑 Add Admin",
                callback_data="owner_addadmin"
            ),
            InlineKeyboardButton(
                "🛒 Add Seller",
                callback_data="owner_addseller"
            )
        ],
        [
            InlineKeyboardButton(
                "💎 Add Premium",
                callback_data="owner_addprem"
            ),
            InlineKeyboardButton(
                "📣 Broadcast",
                callback_data="owner_bc"
            )
        ],
        [
            InlineKeyboardButton(
                "📊 Stats",
                callback_data="owner_stats"
            )
        ]
    ]
)

# =========================================
# ADMIN PANEL BUTTON
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
# SELLER PANEL BUTTON
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
async def panel(_, msg):

    user_id = msg.from_user.id
    role = get_role(user_id)

    # OWNER
    if role == "OWNER":

        return await msg.reply(
            """
👑 OWNER PANEL

Available Access:
• Add Admin
• Add Seller
• Add Premium
• Broadcast
• Full Control
""",
            reply_markup=OWNER_PANEL
        )

    # ADMIN
    elif role == "ADMIN":

        return await msg.reply(
            """
🛠 ADMIN PANEL

Available Access:
• Add Seller
• Add Premium
""",
            reply_markup=ADMIN_PANEL
        )

    # SELLER
    elif role == "SELLER":

        return await msg.reply(
            """
🛒 SELLER PANEL

Available Access:
• Add Premium
""",
            reply_markup=SELLER_PANEL
        )

    # PREM / FREE
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
# DEL ADMIN
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
# DEL SELLER
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
# DEL PREMIUM
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
# OWNER CALLBACKS
# =========================================

@app.on_callback_query()
async def owner_callbacks(_, query):

    data = query.data
    user_id = query.from_user.id
    role = get_role(user_id)

    # OWNER CALLBACK
    if role == "OWNER":

        if data == "owner_addadmin":

            return await query.message.reply(
                """
👑 ADD ADMIN

Command:
/addadmin user_id
"""
            )

        elif data == "owner_addseller":

            return await query.message.reply(
                """
🛒 ADD SELLER

Command:
/addseller user_id
"""
            )

        elif data == "owner_addprem":

            return await query.message.reply(
                """
💎 ADD PREMIUM

Command:
/addprem user_id
"""
            )

        elif data == "owner_bc":

            return await query.message.reply(
                """
📣 BROADCAST

Command:
/bc pesan
"""
            )

        elif data == "owner_stats":

            return await query.message.reply(
                """
📊 BOT STATS

System Online ✅
"""
            )

    # ADMIN CALLBACK
    elif role == "ADMIN":

        if data == "admin_addseller":

            return await query.message.reply(
                """
🛒 ADD SELLER

Command:
/addseller user_id
"""
            )

        elif data == "admin_addprem":

            return await query.message.reply(
                """
💎 ADD PREMIUM

Command:
/addprem user_id
"""
            )

    # SELLER CALLBACK
    elif role == "SELLER":

        if data == "seller_addprem":

            return await query.message.reply(
                """
💎 ADD PREMIUM

Command:
/addprem user_id
"""
            )

# =========================================
# HELP MENU
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

👑 OWNER:
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

🛠 ADMIN:
• /panel
• /addseller
• /delseller
• /addprem
• /delprem
"""

    elif role == "SELLER":

        text += """

🛒 SELLER:
• /panel
• /addprem
• /delprem
"""

    elif role == "PREM":

        text += """

💎 PREMIUM:
• /help
• /afk
"""

    else:

        text += """

❌ FREE USER
"""

    await msg.reply(text)
