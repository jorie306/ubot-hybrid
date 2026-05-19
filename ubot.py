import os
import datetime
import json
from telethon import TelegramClient, events, Button

# Environment Variables
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

# Initialize Bot & Userbot
bot = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
userbot = TelegramClient("user_session", API_ID, API_HASH)

# Data Storage
login_state = {}
premium_users = {}  # {user_id: expiry_datetime}
seller_users = set()
auto_replies = {}  # {chat_id: {"texts": [], "channels": [], "items": [], "active": bool}}
autobc_config = {}  # {user_id: {"basic": {"list": [], "rounds": 1, "active": False}, "forward": {"list": [], "rounds": 1, "active": False}}}
blacklist = set()

# ==================== HELPER FUNCTIONS ====================
def is_owner(user_id):
    return user_id == OWNER_ID

def is_seller(user_id):
    return user_id in seller_users

def is_premium(user_id):
    if user_id not in premium_users:
        return False
    if premium_users[user_id] == "lifetime":
        return True
    return datetime.datetime.now() < premium_users[user_id]

def has_access(user_id):
    return is_owner(user_id) or is_seller(user_id) or is_premium(user_id)

# ==================== START MENU ====================
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender_id
    buttons = [
        [Button.text("🔑 Buat Userbot")],
        [Button.text("📜 Ketentuan")],
        [Button.text("📖 Tutor")]
    ]
    
    if is_owner(user_id):
        buttons.extend([
            [Button.text("👑 Owner Panel")],
        ])
    elif is_seller(user_id):
        buttons.extend([
            [Button.text("💼 Seller Panel")],
        ])
    elif is_premium(user_id):
        buttons.extend([
            [Button.text("⭐ Premium Panel")],
        ])
    
    await event.respond("🌟 Selamat datang!\n\nSilakan pilih menu:", buttons=buttons)

# ==================== LOGIN FLOW ====================
@bot.on(events.NewMessage(pattern='Buat Userbot'))
async def login_start(event):
    user_id = event.sender_id
    await event.respond("Masukkan nomor telepon kamu (format: +62xxx):")
    login_state[user_id] = {"step": "phone"}

@bot.on(events.NewMessage)
async def login_flow(event):
    user_id = event.sender_id
    
    if user_id not in login_state:
        return
    
    step = login_state[user_id]["step"]
    
    if step == "phone":
        phone = event.raw_text.strip()
        login_state[user_id]["phone"] = phone
        try:
            await userbot.connect()
            await userbot.send_code_request(phone)
            login_state[user_id]["step"] = "code"
            await event.respond("✅ Kode OTP sudah dikirim, masukkan di sini:")
        except Exception as e:
            await event.respond(f"❌ Error: {e}")
            del login_state[user_id]
    
    elif step == "code":
        code = event.raw_text.strip()
        phone = login_state[user_id]["phone"]
        try:
            await userbot.sign_in(phone, code)
            login_state[user_id]["step"] = "success"
            await event.respond("✅ Userbot berhasil dibuat! Session tersimpan.")
            del login_state[user_id]
        except Exception as e:
            if "PASSWORD" in str(e):
                login_state[user_id]["step"] = "password"
                await event.respond("🔐 Akun ini pakai 2FA. Masukkan password:")
            else:
                await event.respond(f"❌ Gagal login: {e}")
    
    elif step == "password":
        pwd = event.raw_text.strip()
        phone = login_state[user_id]["phone"]
        try:
            await userbot.sign_in(phone, password=pwd)
            await event.respond("✅ Userbot berhasil dibuat dengan 2FA! Session tersimpan.")
            del login_state[user_id]
        except Exception as e:
            await event.respond(f"❌ Password salah: {e}")

# ==================== INFO MENU ====================
@bot.on(events.NewMessage(pattern='Ketentuan'))
async def ketentuan(event):
    await event.respond(
        "📜 **KETENTUAN PENGGUNAAN**\n\n"
        "✅ Gunakan bot sesuai aturan Telegram\n"
        "❌ Jangan spam atau abuse\n"
        "⏰ Premium aktif sesuai durasi\n"
        "📞 Hubungi Owner/Seller untuk perpanjangan\n"
        "🚫 Pelanggaran = banned permanen"
    )

@bot.on(events.NewMessage(pattern='Tutor'))
async def tutor(event):
    await event.respond(
        "📖 **TUTORIAL PENGGUNAAN**\n\n"
        "**1. Buat Userbot:**\n"
        "• Klik 'Buat Userbot'\n"
        "• Masukkan nomor telepon\n"
        "• Masukkan OTP & password 2FA\n\n"
        "**2. AutoBC (Broadcast):**\n"
        "• `.autobc basic save` - Simpan pesan\n"
        "• `.autobc rounds 180` - Set delay\n"
        "• `.autobc basic on/off` - Aktif/Nonaktif\n\n"
        "**3. AutoReply:**\n"
        "• `/addtext` - Simpan text balasan\n"
        "• `/addchannel` - Tambah channel\n"
        "• `/additem` - Tambah kata kunci\n"
        "• `/wtb on/off` - Aktif/Nonaktif\n\n"
        "**4. Blacklist:**\n"
        "• `.addnl` - Blacklist GC/Channel\n"
        "• `.delbl` - Hapus dari blacklist"
    )

# ==================== AUTOBC FEATURE ====================
@bot.on(events.NewMessage(pattern=r'\.autobc'))
async def autobc_handler(event):
    user_id = event.sender_id
    
    if not has_access(user_id):
        await event.respond("❌ Kamu tidak punya akses AutoBC.")
        return
    
    if user_id not in autobc_config:
        autobc_config[user_id] = {
            "basic": {"list": [], "rounds": 1, "active": False},
            "forward": {"list": [], "rounds": 1, "active": False}
        }
    
    cmd = event.raw_text.lower().split()
    
    try:
        if len(cmd) >= 3 and cmd[1] == "basic" and cmd[2] == "save":
            msg = event.raw_text.split(" ", 3)[-1]
            autobc_config[user_id]["basic"]["list"].append(msg)
            await event.respond(f"✅ Pesan disimpan untuk AutoBC Basic.\nTotal: {len(autobc_config[user_id]['basic']['list'])} pesan")
        
        elif len(cmd) >= 3 and cmd[1] == "basic" and cmd[2] == "rounds":
            rounds = int(cmd[3])
            if rounds < 1:
                await event.respond("❌ Minimal 1 detik")
                return
            autobc_config[user_id]["basic"]["rounds"] = rounds
            await event.respond(f"✅ Delay AutoBC Basic diatur {rounds} detik.")
        
        elif len(cmd) >= 3 and cmd[1] == "basic" and cmd[2] in ["on", "off"]:
            autobc_config[user_id]["basic"]["active"] = (cmd[2] == "on")
            status = "✅ AKTIF" if cmd[2] == "on" else "❌ NONAKTIF"
            await event.respond(f"{status} - AutoBC Basic")
        
        elif len(cmd) >= 3 and cmd[1] == "forward" and cmd[2] == "save":
            msg = event.raw_text.split(" ", 3)[-1]
            autobc_config[user_id]["forward"]["list"].append(msg)
            await event.respond(f"✅ Pesan forward disimpan.\nTotal: {len(autobc_config[user_id]['forward']['list'])} pesan")
        
        elif len(cmd) >= 3 and cmd[1] == "forward" and cmd[2] == "rounds":
            rounds = int(cmd[3])
            if rounds < 1:
                await event.respond("❌ Minimal 1 detik")
                return
            autobc_config[user_id]["forward"]["rounds"] = rounds
            await event.respond(f"✅ Delay AutoBC Forward diatur {rounds} detik.")
        
        elif len(cmd) >= 3 and cmd[1] == "forward" and cmd[2] in ["on", "off"]:
            autobc_config[user_id]["forward"]["active"] = (cmd[2] == "on")
            status = "✅ AKTIF" if cmd[2] == "on" else "❌ NONAKTIF"
            await event.respond(f"{status} - AutoBC Forward")
        
        else:
            await event.respond(
                "❌ Command tidak valid.\n\n"
                "Format:\n"
                "`.autobc basic save` - Simpan pesan\n"
                "`.autobc basic rounds <detik>` - Set delay\n"
                "`.autobc basic on/off` - Aktif/Nonaktif\n"
                "`.autobc forward save` - Simpan forward\n"
                "`.autobc forward rounds <detik>` - Set delay\n"
                "`.autobc forward on/off` - Aktif/Nonaktif"
            )
    except Exception as e:
        await event.respond(f"❌ Error: {e}")

# ==================== AUTOREPLY FEATURE ====================
@bot.on(events.NewMessage(pattern=r'/addtext'))
async def addtext(event):
    user_id = event.sender_id
    
    if not has_access(user_id):
        await event.respond("❌ Tidak punya akses.")
        return
    
    try:
        text = event.raw_text.split(" ", 1)[1]
        cid = event.chat_id
        
        if cid not in auto_replies:
            auto_replies[cid] = {"texts": [], "channels": [], "items": [], "active": False}
        
        auto_replies[cid]["texts"].append(text)
        await event.respond(f"✅ Text balasan ditambahkan.\nTotal: {len(auto_replies[cid]['texts'])} text")
    except:
        await event.respond("❌ Format: /addtext <text balasan>")

@bot.on(events.NewMessage(pattern=r'/addchannel'))
async def addchannel(event):
    user_id = event.sender_id
    
    if not has_access(user_id):
        await event.respond("❌ Tidak punya akses.")
        return
    
    try:
        channel = event.raw_text.split(" ", 1)[1]
        cid = event.chat_id
        
        if cid not in auto_replies:
            auto_replies[cid] = {"texts": [], "channels": [], "items": [], "active": False}
        
        auto_replies[cid]["channels"].append(channel)
        await event.respond(f"✅ Channel ditambahkan.\nTotal: {len(auto_replies[cid]['channels'])} channel")
    except:
        await event.respond("❌ Format: /addchannel <channel_id atau @username>")

@bot.on(events.NewMessage(pattern=r'/additem'))
async def additem(event):
    user_id = event.sender_id
    
    if not has_access(user_id):
        await event.respond("❌ Tidak punya akses.")
        return
    
    try:
        item = event.raw_text.split(" ", 1)[1].lower()
        cid = event.chat_id
        
        if cid not in auto_replies:
            auto_replies[cid] = {"texts": [], "channels": [], "items": [], "active": False}
        
        if len(auto_replies[cid]["items"]) >= 20:
            await event.respond("❌ Maksimal 20 item.")
            return
        
        auto_replies[cid]["items"].append(item)
        await event.respond(f"✅ Item '{item}' ditambahkan.\nTotal: {len(auto_replies[cid]['items'])}/20")
    except:
        await event.respond("❌ Format: /additem <kata_kunci>")

@bot.on(events.NewMessage(pattern=r'/wtb'))
async def wtb(event):
    user_id = event.sender_id
    
    if not has_access(user_id):
        await event.respond("❌ Tidak punya akses.")
        return
    
    try:
        cmd = event.raw_text.split()[1].lower()
        cid = event.chat_id
        
        if cid not in auto_replies:
            auto_replies[cid] = {"texts": [], "channels": [], "items": [], "active": False}
        
        auto_replies[cid]["active"] = (cmd == "on")
        status = "✅ AKTIF" if cmd == "on" else "❌ NONAKTIF"
        await event.respond(f"{status} - AutoReply")
    except:
        await event.respond("❌ Format: /wtb on/off")

@bot.on(events.NewMessage)
async def autoreply(event):
    cid = event.chat_id
    
    if cid not in auto_replies or not auto_replies[cid]["active"]:
        return
    
    if not auto_replies[cid]["texts"] or not auto_replies[cid]["items"]:
        return
    
    for item in auto_replies[cid]["items"]:
        if item in event.raw_text.lower():
            for text in auto_replies[cid]["texts"]:
                await event.reply(text)
            break

# ==================== BLACKLIST FEATURE ====================
@bot.on(events.NewMessage(pattern=r'\.addnl'))
async def addnl(event):
    user_id = event.sender_id
    
    if not has_access(user_id):
        await event.respond("❌ Tidak punya akses.")
        return
    
    blacklist.add(event.chat_id)
    await event.respond("✅ Channel/GC masuk blacklist.")

@bot.on(events.NewMessage(pattern=r'\.delbl'))
async def delbl(event):
    user_id = event.sender_id
    
    if not has_access(user_id):
        await event.respond("❌ Tidak punya akses.")
        return
    
    blacklist.discard(event.chat_id)
    await event.respond("✅ Channel/GC dihapus dari blacklist.")

# ==================== OWNER COMMANDS ====================
@bot.on(events.NewMessage(pattern='/addseller'))
async def add_seller(event):
    if not is_owner(event.sender_id):
        await event.respond("❌ Hanya Owner.")
        return
    
    try:
        user_id = int(event.raw_text.split()[1])
        seller_users.add(user_id)
        await event.respond(f"✅ User {user_id} jadi Seller.")
    except:
        await event.respond("❌ Format: /addseller <user_id>")

@bot.on(events.NewMessage(pattern='/delseller'))
async def del_seller(event):
    if not is_owner(event.sender_id):
        await event.respond("❌ Hanya Owner.")
        return
    
    try:
        user_id = int(event.raw_text.split()[1])
        seller_users.discard(user_id)
        await event.respond(f"✅ User {user_id} dihapus dari Seller.")
    except:
        await event.respond("❌ Format: /delseller <user_id>")

@bot.on(events.NewMessage(pattern='/addprem'))
async def add_prem(event):
    if not (is_owner(event.sender_id) or is_seller(event.sender_id)):
        await event.respond("❌ Hanya Owner/Seller.")
        return
    
    try:
        parts = event.raw_text.split()
        if len(parts) < 3:
            await event.respond("❌ Format: /addprem <user_id1> <user_id2> ... <durasi_hari atau 'lifetime'>")
            return
        
        durasi = parts[-1].lower()
        user_ids = parts[1:-1]
        
        if durasi == "lifetime":
            expiry = "lifetime"
        else:
            days = int(durasi)
            if days < 1:
                await event.respond("❌ Minimal 1 hari.")
                return
            expiry = datetime.datetime.now() + datetime.timedelta(days=days)
        
        for uid_str in user_ids:
            uid = int(uid_str)
            premium_users[uid] = expiry
        
        if expiry == "lifetime":
            await event.respond(f"✅ Premium LIFETIME diberikan ke {len(user_ids)} user.")
        else:
            await event.respond(f"✅ Premium diberikan ke {len(user_ids)} user sampai {expiry.strftime('%d-%m-%Y')}.")
    except Exception as e:
        await event.respond(f"❌ Error: {e}")

@bot.on(events.NewMessage(pattern='/delprem'))
async def del_prem(event):
    if not is_owner(event.sender_id):
        await event.respond("❌ Hanya Owner.")
        return
    
    try:
        user_id = int(event.raw_text.split()[1])
        if user_id in premium_users:
            del premium_users[user_id]
            await event.respond(f"✅ Premium user {user_id} dihapus.")
        else:
            await event.respond("❌ User tidak premium.")
    except:
        await event.respond("❌ Format: /delprem <user_id>")

@bot.on(events.NewMessage(pattern='/deluser'))
async def del_user(event):
    if not is_owner(event.sender_id):
        await event.respond("❌ Hanya Owner.")
        return
    
    try:
        user_id = int(event.raw_text.split()[1])
        
        # Hapus dari semua list
        seller_users.discard(user_id)
        if user_id in premium_users:
            del premium_users[user_id]
        if user_id in autobc_config:
            del autobc_config[user_id]
        if user_id in login_state:
            del login_state[user_id]
        
        await event.respond(f"✅ User {user_id} dihapus dari sistem.")
    except:
        await event.respond("❌ Format: /deluser <user_id>")

# ==================== START BOT ====================
print("🤖 Ubot sedang berjalan...")
bot.run_until_disconnected()
