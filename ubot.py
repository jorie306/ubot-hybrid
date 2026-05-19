import os
from telethon import TelegramClient, events, Button

# Ambil API dari Environment Variables
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

OWNER = os.environ.get("OWNER", "Owner belum diatur")
SELLER = os.environ.get("SELLER", "Seller belum diatur")

# Inisialisasi bot
bot = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Inisialisasi userbot (login dengan nomor telepon sekali secara lokal)
userbot = TelegramClient("user_session", API_ID, API_HASH)

async def start_userbot():
    await userbot.start()  # akan minta nomor telepon + kode OTP saat pertama kali dijalankan
    print("Userbot aktif!")

# Database sederhana untuk akses premium/seller
premium_users = set()
seller_users = set()

# Handler untuk /start
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond(
        "🌟 Selamat datang di Userbot!\n\n"
        "Bot ini siap membantu kamu dengan berbagai fitur praktis. "
        "Gunakan menu di bawah untuk mulai eksplorasi.\n\n"
        "Dengan bot ini, kamu bisa melakukan broadcast otomatis, auto reply, "
        "akses premium, dan berbagai fungsi lainnya. 🚀",
        buttons=[
            [Button.text("📢 AutoBC"), Button.text("🤖 AutoReply")],
            [Button.text("👑 Owner"), Button.text("💼 Seller")],
            [Button.text("⭐ Premium"), Button.text("📜 Ketentuan")],
            [Button.text("📖 Tutor")]
        ]
    )

# Handler tombol Owner
@bot.on(events.NewMessage(pattern='Owner'))
async def owner(event):
    await event.respond(f"👑 Owner: {OWNER}")

# Handler tombol Seller
@bot.on(events.NewMessage(pattern='Seller'))
async def seller(event):
    await event.respond(f"💼 Seller: {SELLER}")

# Handler tombol Premium
@bot.on(events.NewMessage(pattern='Premium'))
async def premium(event):
    if str(event.sender_id) in premium_users:
        await event.respond("⭐ Kamu sudah memiliki akses Premium.")
    else:
        await event.respond("❌ Kamu belum memiliki akses Premium. Hubungi Owner/Seller untuk mendapatkannya.")

# Command untuk Owner memberikan akses Seller
@bot.on(events.NewMessage(pattern='/addseller'))
async def add_seller(event):
    if str(event.sender_id) == OWNER:
        try:
            user_id = int(event.raw_text.split()[1])
            seller_users.add(str(user_id))
            await event.respond(f"✅ User {user_id} sekarang menjadi Seller.")
        except:
            await event.respond("Format salah. Gunakan: /addseller <user_id>")
    else:
        await event.respond("❌ Hanya Owner yang bisa memberikan akses Seller.")

# Command untuk Owner/Seller memberikan akses Premium
@bot.on(events.NewMessage(pattern='/addprem'))
async def add_prem(event):
    if str(event.sender_id) == OWNER or str(event.sender_id) in seller_users:
        try:
            user_id = int(event.raw_text.split()[1])
            premium_users.add(str(user_id))
            await event.respond(f"✅ User {user_id} sekarang memiliki akses Premium.")
        except:
            await event.respond("Format salah. Gunakan: /addprem <user_id>")
    else:
        await event.respond("❌ Hanya Owner atau Seller yang bisa memberikan akses Premium.")

# Handler AutoBC
@bot.on(events.NewMessage(pattern='AutoBC'))
async def autobc(event):
    await event.respond("📢 Auto Broadcast aktif: semua pesan akan otomatis dikirim ke grup/channel yang kamu kelola.")

# Handler AutoReply
@bot.on(events.NewMessage(pattern='AutoReply'))
async def autoreply(event):
    await event.respond("🤖 Auto Reply aktif: bot akan otomatis membalas pesan sesuai pola yang kamu tentukan.")

# Auto Reply sederhana
@bot.on(events.NewMessage)
async def auto_reply(event):
    if "halo" in event.raw_text.lower():
        await event.reply("Hai 👋, ada yang bisa saya bantu?")
    elif "thanks" in event.raw_text.lower():
        await event.reply("Sama-sama 🙏")

# Handler Ketentuan
@bot.on(events.NewMessage(pattern='Ketentuan'))
async def ketentuan(event):
    await event.respond("📜 Ketentuan penggunaan:\n\n1. Jangan spam.\n2. Gunakan fitur dengan bijak.\n3. Hormati privasi orang lain.")

# Handler Tutor
@bot.on(events.NewMessage(pattern='Tutor'))
async def tutor(event):
    await event.respond("📖 Tutor: panduan penggunaan bot ini akan ditampilkan di sini.")

print("Bot sedang berjalan...")

# Jalankan bot
bot.run_until_disconnected()

