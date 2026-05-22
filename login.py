import os

from pyrogram import Client, filters
from pyrogram.errors import SessionPasswordNeeded

# =========================================
# TEMP LOGIN
# =========================================

LOGIN_DATA = {}

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# =========================================
# LOAD LOGIN SYSTEM
# =========================================

def load_login(app):

    # =====================================
    # /login
    # =====================================

    @app.on_message(filters.command("login"))
    async def login_cmd(_, msg):

        user_id = msg.from_user.id

        LOGIN_DATA[user_id] = {
            "step": "phone"
        }

        await msg.reply(
            """
📲 LOGIN USERBOT

Kirim nomor Telegram kamu.

Contoh:
+628123456789
"""
        )

    # =====================================
    # HANDLE LOGIN
    # =====================================

    @app.on_message(
        filters.private & ~filters.command(
            ["start", "ping", "login"]
        )
    )
    async def login_handler(_, msg):

        user_id = msg.from_user.id

        if user_id not in LOGIN_DATA:
            return

        data = LOGIN_DATA[user_id]

        # =================================
        # STEP PHONE
        # =================================

        if data["step"] == "phone":

            phone = msg.text.strip()

            session_name = f"sessions/{user_id}"

            client = Client(
                session_name,
                api_id=API_ID,
                api_hash=API_HASH
            )

            await client.connect()

            try:

                code = await client.send_code(
                    phone
                )

            except Exception as e:

                await msg.reply(
                    f"""
❌ Nomor tidak valid

Gunakan format:
+628xxxx

Error:
{e}
"""
                )

                await client.disconnect()

                del LOGIN_DATA[user_id]

                return

            LOGIN_DATA[user_id] = {
                "step": "code",
                "phone": phone,
                "phone_code_hash": code.phone_code_hash,
                "client": client
            }

            return await msg.reply(
                """
✅ OTP terkirim

Kirim kode OTP.

Contoh:
1 2 3 4 5
"""
            )

        # =================================
        # STEP CODE
        # =================================

        elif data["step"] == "code":

            code = msg.text.replace(
                " ",
                ""
            )

            client = data["client"]

            try:

                await client.sign_in(
                    phone_number=data["phone"],
                    phone_code_hash=data["phone_code_hash"],
                    phone_code=code
                )

                await msg.reply(
                    """
✅ LOGIN BERHASIL

👑 Userbot aktif
"""
                )

                await client.disconnect()

                del LOGIN_DATA[user_id]

            except SessionPasswordNeeded:

                LOGIN_DATA[user_id]["step"] = "password"

                await msg.reply(
                    """
🔒 Akun memakai 2FA

Kirim password Telegram kamu.
"""
                )

            except Exception as e:

                await msg.reply(
                    f"""
❌ OTP salah

Error:
{e}
"""
                )

        # =================================
        # STEP PASSWORD
        # =================================

        elif data["step"] == "password":

            client = data["client"]

            try:

                await client.check_password(
                    msg.text
                )

                await msg.reply(
                    """
✅ LOGIN BERHASIL

👑 Userbot aktif
"""
                )

                await client.disconnect()

                del LOGIN_DATA[user_id]

            except Exception as e:

                await msg.reply(
                    f"""
❌ Password salah

Error:
{e}
"""
                )
