import os
import datetime
from telethon import TelegramClient, events, Button

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

OWNER = os.environ.get("OWNER", "0")  # user_id Owner
SELLER = os.environ.get("SELLER", "0")  # user_id Seller default

bot = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
userbot = TelegramClient("user_session", API_ID, API_HASH)

async def start_userbot():
    await userbot.start()
    print("✅ Userbot aktif!")

# Database
premium_users = {}   # {user_id: expiry_date}
seller_users = {SELLER} if SELLER != "0" else set()
auto_replies = {}    # {channel_id: {"items":[], "texts":[], "wtb":False}}
autobc_config = {"list":[], "rounds":1, "active":False, "forward":False}
blacklist = set()

# ---------------- MENU START ----------------
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond(
        "🌟 Selamat datang!\n\n"
        "Gunakan menu di bawah untuk eksplorasi fitur 🚀",
        buttons=[
            [Button.text("📢 AutoBC"), Button.text("🤖 AutoReply")],
            [Button.text("👑 Owner"), Button.text("💼 Seller")],
            [Button.text("⭐ Premium"), Button.text("📜 Ketentuan")],
            [Button.text("📖 Tutor"), Button.text("🔄 Buat Ulang Userbot")]
        ]
    )

# ---------------- AUTOBC ----------------
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

# ---------------- AUTOREPLY ----------------
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

@bot.on(events.NewMessage(pattern=r'/addchannel'))
async def addchannel(event):
    cid = event.chat_id
    auto_replies.setdefault(cid, {"items":[],"texts":[],"wtb":False})
    await event.respond("✅ Channel ditambahkan untuk AutoReply.")

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
        await event.respond("❌ Tidak punya akses.")

@bot.on(events.NewMessage(pattern='/delprem'))
async def del_prem(event):
    if str(event.sender_id) == OWNER or str(event.sender_id) in seller_users:
        user_id = event.raw_text.split()[1]
        premium_users.pop(user_id, None)
        await event.respond(f"❌ Premium user {user_id} dicabut.")
    else:
        await event.respond("❌ Tidak punya akses.")

@bot.on(events.NewMessage(pattern='/checkprem'))
async def check_prem(event):
    if str(event.sender_id) == OWNER or str(event.sender_id) in seller_users:
        user_id = event.raw_text.split()[1]
        if user_id in premium_users and premium_users[user_id] > datetime.datetime.now():
            exp = premium_users[user_id].strftime("%d-%m-%Y %H:%M")
            await event.respond(f"⭐ User {user_id} Premium sampai {exp}")
        else:
            await event.respond(f"❌ User {user_id} tidak Premium atau sudah kadaluarsa.")
    else:
        await event.respond("❌ Tidak punya akses.")

# ---------------- RESET PREMIUM ----------------
@bot.on(events.NewMessage(pattern='Buat Ulang Userbot'))
async def reset_userbot(event):
    uid = str(event.sender_id)
    if uid in premium_users and premium_users[uid] > datetime.datetime.now():
        expiry = premium_users[uid]
        premium_users[uid] = expiry  # reset ulang
        await event.respond("🔄 Userbot kamu berhasil dibuat ulang. Premium tetap aktif sampai "
                            f"{expiry.strftime('%d-%m-%Y %H:%M')}")
    else:
        await event.respond("❌ Durasi Premium kamu sudah habis. Hubungi Owner/Seller untuk perpanjangan.")

print("🚀 Bot berjalan...")
bot.run_until_disconnected()
