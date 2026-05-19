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
            [Button.text("🔑 Buat Userbot")],
            [Button.text("📜 Ketentuan")],
            [Button.text("📖 Tutor")]
        ]
    )

# ---------------- LOGIN FLOW ----------------
@bot.on(events.NewMessage(pattern='Buat Userbot'))
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
                await event.respond("✅ Userbot berhasil dibuat! Session tersimpan.")
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
                await event.respond("✅ Userbot berhasil dibuat dengan 2FA! Session tersimpan.")
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
        "1. Klik Buat Userbot untuk login akun Telegram.\n"
        "2. Masukkan nomor telepon, OTP, dan password 2FA.\n"
        "3. Setelah login, session tersimpan otomatis.\n"
        "4. Gunakan fitur AutoBC, AutoReply, Blacklist, Premium sesuai kebutuhan."
    )

# ---------------- FITUR AUTOBC ----------------
@bot.on(events.NewMessage(pattern=r'\.autobc'))
async def autobc_handler(event):
    if str(event.sender_id) == OWNER or str(event.sender_id) in seller_users or str(event.sender_id) in premium_users:
        cmd = event.raw_text.lower().split()
        if len(cmd) >= 3 and cmd[1] == "basic" and cmd[2] == "save":
            autobc_config["list"].append(event.raw_text.split(" ",3)[-1])
            await event.respond("✅ Pesan disimpan untuk AutoBC Basic.")
        elif len(cmd) >= 3 and cmd[1] == "rounds":
            try:
                delay = int(cmd[2])
                autobc_config["rounds"] = max(1, delay)
                await event.respond(f"✅ Delay AutoBC diatur {delay} detik.")
            except:
                await event.respond("Format: .autobc rounds <detik>")
        elif len(cmd) >= 3 and cmd[1] == "basic" and cmd[2] in ["on","off"]:
            autobc_config["active"] = (cmd[2] == "on")
            await event.respond(f"✅ AutoBC Basic {'aktif' if cmd[2]=='on' else 'nonaktif'}.")
        elif len(cmd) >= 3 and cmd[1] == "forward" and cmd[2] == "save":
            autobc_config["forward"] = True
            autobc_config["list"].append(event.raw_text.split(" ",3)[-1])
            await event.respond("✅ Pesan forward disimpan untuk AutoBC.")
        else:
            await event.respond("❌ Command AutoBC tidak valid.")
    else:
        await event.respond("❌ Kamu tidak punya akses AutoBC.")

# ---------------- FITUR AUTOREPLY ----------------
@bot.on(events.NewMessage(pattern=r'/addtext'))
async def addtext(event):
    if str(event.sender_id) == OWNER or str(event.sender_id) in seller_users or str(event.sender_id) in premium_users:
        text = event.raw_text.split(" ",1)[1]
        cid = event.chat_id
        auto_replies.setdefault(cid, {"items":[],"texts":[],"wtb":False})
        auto_replies[cid]["texts"].append(text)
        await event.respond("✅ Text balasan ditambahkan.")
    else:
        await event.respond("❌ Tidak punya akses.")

@bot.on(events.NewMessage(pattern=r'/additem'))
async def additem(event):
    cid = event.chat_id
    auto_replies.setdefault(cid, {"items":[],"texts":[],"wtb":False})
    item = event.raw_text.split(" ",1)[1].lower()
    if len(auto_replies[cid]["items"]) < 20:
        auto_replies[cid]["items"].append(item)
        await event.respond(f"✅ Item '{item}' ditambahkan.")
    else:
        await event.respond("❌ Maksimal 20 item.")

@bot.on(events.NewMessage(pattern=r'/wtb'))
async def wtb(event):
    cmd = event.raw_text.split()[1].lower()
    cid = event.chat_id
    auto_replies.setdefault(cid, {"items":[],"texts":[],"wtb":False})
    auto_replies[cid]["wtb"] = (cmd=="on")
    await event.respond(f"✅ AutoReply {'aktif' if cmd=='on' else 'nonaktif'}.")

@bot.on(events.NewMessage)
async def autoreply(event):
    cid = event.chat_id
    if cid in auto_replies and auto_replies[cid]["wtb"]:
        for item in auto_replies[cid]["items"]:
            if item in event.raw_text.lower():
                for text in auto_replies[cid]["texts"]:
                    await event.reply(text)
                break

# ---------------- BLACKLIST ----------------
@bot.on(events.NewMessage(pattern=r'\.addnl'))
async def addnl(event):
    blacklist.add(event.chat_id)
    await event.respond("✅ Channel/GC masuk blacklist.")

@bot.on(events.NewMessage(pattern=r'\.delbl'))
async def delbl(event):
    blacklist.discard(event.chat_id)
    await event.respond("✅ Channel/GC dihapus dari blacklist.")

# ---------------- OWNER/SELLER/PREMIUM ----------------
@bot.on(events.NewMessage(pattern='/addseller'))
async def add_seller(event):
    if str(event.sender_id) == OWNER:
        user_id = event.raw_text.split()[1]
        seller_users.add(user_id)
        await event.respond(f"✅ User {user_id} jadi Seller.")
    else:
        await event.respond("❌ Hanya Owner bisa tambah Seller.")

@bot.on(events.NewMessage(pattern='/addprem'))
async def add_prem(event):
    if str(event.sender_id) == OWNER or str(event.sender_id) in seller_users:
        parts = event.raw_text.split()
        user_ids = parts[1:-1]
        days = int(parts[-1])
        if days < 1:
            await event.respond("❌ Durasi Premium minimal 1 hari.")
            return
        expiry = datetime.datetime.now() + datetime.timedelta(days=days)
        for uid in user_ids:
            premium_users[uid] = expiry
        await event.respond(f"✅ Premium diberikan ke {len(user_ids)} user sampai {expiry}.")
    else:
        await event.respond("❌ Hanya Owner/Seller bisa tambah Premium.")

bot.run_until_disconnected()
