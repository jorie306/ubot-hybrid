from telethon import TelegramClient, events, Button
import os

# Ambil dari environment Railway (atau bisa langsung hardcode)
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")

# Userbot session (akun pribadi)
userbot = TelegramClient('user_session', api_id, api_hash)

# Bot resmi (BotFather)
bot = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

LOGIN_CODE = "v2langkah"
userbot_active = False

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond(
        "👋 Selamat datang!\nKlik tombol untuk mulai userbot:",
        buttons=[
            [Button.inline("▶️ Mulai Userbot", b"mulai")],
            [Button.url("📜 Ketentuan", "https://t.me/tutorubotjorie")],
            [Button.url("🛒 Store", "https://t.me/vablid")],
            [Button.url("📚 Tutor", "https://t.me/tutorubotjorie")]
        ]
    )

@bot.on(events.CallbackQuery(data=b"mulai"))
async def mulai(event):
    await event.respond("🔑 Masukkan kode login untuk aktifkan Userbot:")

@bot.on(events.NewMessage)
async def kode(event):
    global userbot_active
    if event.raw_text.strip() == LOGIN_CODE:
        userbot_active = True
        await event.reply("✅ Userbot diaktifkan!")
        async with userbot:
            await userbot.send_message("me", "Userbot sudah aktif!")

print("Bot sedang berjalan...")
bot.run_until_disconnected()
