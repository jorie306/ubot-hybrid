import os
import datetime
from telethon import TelegramClient, events, Button

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

OWNER = os.environ.get("OWNER", "0")
SELLER = os.environ.get("SELLER", "0")

bot = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
userbot = TelegramClient("user_session", API_ID, API_HASH)

login_state = {}
premium_users = {}
seller_users = {SELLER} if SELLER != "0" else set()
auto_replies = {}
autobc_config = {"list":[], "rounds":1, "active":False, "forward":False}
blacklist = set()

# ---------------- START MENU ----------------
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond(
        "🌟 Selamat datang!\n\nSilakan pilih menu:",
        buttons=[
            [Button.text("🔑 Login Session")],
            [Button.text("📜 Ketentuan")],
            [Button.text("📖 Tutor")]
        ]
    )

# ---------------- LOGIN FLOW ----------------
@bot.on(events.NewMessage(pattern='Login Session'))
async def login_start(event):
    await event.respond("Masukkan nomor telepon kamu (format: +62xxx):")
    login_state[event.sender_id] = {"step": "phone"}

@bot.on(events.NewMessage)
async def login_flow(event):
    uid = event.sender_id
    if uid in login_state:
        step = login_state[uid]["step"]

        if step == "phone":
            phone = event.raw_text.strip()
            login_state[uid]["phone"] = phone
            await userbot.connect()
            await userbot.send_code_request(phone)
            login_state[uid]["step"] = "code"
            await event.respond("Kode OTP sudah dikirim, masukkan di sini:")

        elif step == "code":
            code = event.raw_text.strip()
            phone = login_state[uid]["phone"]
            try:
                await userbot.sign_in(phone, code)
                await event.respond("✅ Login berhasil! Session tersimpan.")
                del login_state[uid]
            except Exception as e:
                if "PASSWORD" in str(e):
                    login_state[uid]["step"] = "password"
                    await event.respond("Akun ini pakai 2FA. Masukkan password:")
                else:
                    await event.respond(f"❌ Gagal login: {e}")

        elif step == "password":
            pwd = event.raw_text.strip()
            phone = login_state[uid]["phone"]
            try:
                await userbot.sign_in(phone, password=pwd)
                await event.respond("✅ Login berhasil dengan 2FA! Session tersimpan.")
                del login_state[uid]
            except Exception as e:
                await event.respond(f"❌ Password salah: {e}")

# ---------------- KETENTUAN ----------------
@bot.on(events.NewMessage(pattern='Ketentuan'))
async def ketentuan(event):
    await event.respond(
        "📜 Ketentuan:\n"
        "- Gunakan bot sesuai aturan.\n"
        "- Jangan spam.\n"
        "- Premium aktif sesuai durasi.\n"
        "- Hubungi Owner/Seller untuk perpanjangan."
    )

# ---------------- TUTOR ----------------
@bot.on(events.NewMessage(pattern='Tutor'))
async def tutor(event):
    await event.respond(
        "📖 Tutor:\n"
        "1. Klik Login Session untuk login akun Telegram.\n"
        "2. Masukkan nomor telepon, OTP, dan password 2FA.\n"
        "3. Setelah login, session tersimpan otomatis.\n"
        "4. Gunakan fitur AutoBC, AutoReply, Blacklist, Premium sesuai kebutuhan."
    )

# ---------------- FITUR AUTOBC ----------------
@bot.on(events.NewMessage(pattern=r'\.autobc'))
async def autobc_handler(event):
    # Sama seperti sebelumnya: save, on/off, rounds, forward
    ...

# ---------------- FITUR AUTOREPLY ----------------
@bot.on(events.NewMessage(pattern=r'/addtext'))
async def addtext(event):
    ...

# ---------------- FITUR BLACKLIST ----------------
@bot.on(events.NewMessage(pattern=r'\.addnl'))
async def addnl(event):
    ...

# ---------------- OWNER/SELLER/PREMIUM ----------------
@bot.on(events.NewMessage(pattern='/addseller'))
async def add_seller(event):
    ...

@bot.on(events.NewMessage(pattern='/addprem'))
async def add_prem(event):
    ...

@bot.on(events.NewMessage(pattern='/delprem'))
async def del_prem(event):
    ...

@bot.on(events.NewMessage(pattern='/checkprem'))
async def check_prem(event):
    ...

print("🚀 Bot berjalan...")
bot.run_until_disconnected()
