"""
handlers.py — All Telethon event handlers (commands + message listeners).

Registration happens in register_handlers(bot) which is called from bot.py.
"""

import asyncio
import datetime
import logging
from typing import Optional

from telethon import Button, TelegramClient, events
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError

import database as db
from config import (
    AUTOBC_MAX_MESSAGES,
    AUTOBC_MIN_INTERVAL,
    AUTOREPLY_MAX_TRIGGERS,
    CHANNEL_USERNAME,
    LEVEL_NAMES,
    LEVEL_OWNER,
    LEVEL_PREMIUM,
    LEVEL_SELLER,
    LEVEL_USER,
    OWNER_ID,
)

logger = logging.getLogger(__name__)

# ── In-memory AutoBC task registry ───────────────────────────────────────────
# Maps (owner_id, bc_type) → asyncio.Task
_bc_tasks: dict[tuple[int, str], asyncio.Task] = {}


# ═════════════════════════════════════════════════════════════════════════════
# Permission helpers
# ═════════════════════════════════════════════════════════════════════════════

async def _check_blacklist(event) -> bool:
    """Return True (and reply) if the sender is blacklisted."""
    if await db.is_blacklisted(event.sender_id):
        await event.respond(
            "🚫 Kamu telah diblokir dari menggunakan bot ini.\n"
            "Hubungi admin jika ini adalah kesalahan."
        )
        return True
    return False


async def _require_level(event, min_level: int) -> bool:
    """
    Return True if the sender meets min_level.
    Sends an error reply and returns False otherwise.
    """
    level = await db.get_effective_level(event.sender_id)
    if level >= min_level:
        return True

    needed = LEVEL_NAMES.get(min_level, str(min_level))
    await event.respond(f"❌ Akses ditolak. Diperlukan level: **{needed}**.")
    return False


# ═════════════════════════════════════════════════════════════════════════════
# Channel join reminder (soft — never blocks usage)
# ═════════════════════════════════════════════════════════════════════════════

def _channel_reminder() -> str:
    if not CHANNEL_USERNAME:
        return ""
    return (
        f"\n\n💡 *Opsional:* Bergabunglah ke channel kami untuk update terbaru → "
        f"{CHANNEL_USERNAME}"
    )


# ═════════════════════════════════════════════════════════════════════════════
# /start
# ═════════════════════════════════════════════════════════════════════════════

async def cmd_start(event: events.NewMessage.Event) -> None:
    if await _check_blacklist(event):
        return

    user_id = event.sender_id
    level = await db.get_effective_level(user_id)
    level_name = LEVEL_NAMES.get(level, "User")

    buttons = [
        [Button.inline("📖 Bantuan", b"help"), Button.inline("📊 Status", b"status")],
        [Button.inline("📜 Ketentuan", b"terms"), Button.inline("🎓 Tutorial", b"tutorial")],
    ]

    if level >= LEVEL_PREMIUM:
        buttons.append([
            Button.inline("📢 AutoBC", b"autobc_info"),
            Button.inline("💬 AutoReply", b"autoreply_info"),
        ])

    text = (
        "🌟 **Selamat datang di Ubot!**\n\n"
        f"👤 Level kamu: **{level_name}**\n"
        f"🆔 User ID: `{user_id}`\n\n"
        "Gunakan tombol di bawah atau ketik /help untuk daftar perintah."
        + _channel_reminder()
    )
    await event.respond(text, buttons=buttons)


# ═════════════════════════════════════════════════════════════════════════════
# /help
# ═════════════════════════════════════════════════════════════════════════════

async def cmd_help(event: events.NewMessage.Event) -> None:
    if await _check_blacklist(event):
        return

    level = await db.get_effective_level(event.sender_id)

    lines = [
        "📋 **DAFTAR PERINTAH**\n",
        "**Umum:**",
        "• /start — Menu utama",
        "• /help — Daftar perintah ini",
        "• /status — Status akun kamu",
        "• /myautoreply — Lihat AutoReply kamu",
        "• /myautobc — Lihat AutoBC kamu",
    ]

    if level >= LEVEL_PREMIUM:
        lines += [
            "\n**AutoReply (Premium+):**",
            "• /addreply `<trigger>` | `<balasan>` — Tambah aturan AutoReply",
            "• /delreply `<trigger>` — Hapus aturan AutoReply",
            "• /clearreply — Hapus semua AutoReply",
            "\n**AutoBC (Premium+):**",
            "• /addbc `basic|forward` `<pesan>` — Tambah pesan BC",
            "• /delbc `<id>` — Hapus pesan BC",
            "• /setinterval `basic|forward` `<detik>` — Set interval",
            "• /bcstart `basic|forward` — Mulai broadcast",
            "• /bcstop `basic|forward` — Hentikan broadcast",
            "• /addtarget `<chat_id>` — Tambah target BC",
            "• /deltarget `<chat_id>` — Hapus target BC",
        ]

    if level >= LEVEL_SELLER:
        lines += [
            "\n**Seller:**",
            "• /addprem `<user_id>` `<hari|lifetime>` — Beri Premium",
            "• /delprem `<user_id>` — Cabut Premium",
        ]

    if level >= LEVEL_OWNER:
        lines += [
            "\n**Owner:**",
            "• /addseller `<user_id>` — Jadikan Seller",
            "• /delseller `<user_id>` — Cabut Seller",
            "• /addblacklist `<user_id>` [alasan] — Blacklist user",
            "• /delblacklist `<user_id>` — Hapus dari blacklist",
            "• /listblacklist — Lihat daftar blacklist",
            "• /listusers — Lihat semua user terdaftar",
            "• /broadcast `<pesan>` — Kirim pesan ke semua user",
            "• /deluser `<user_id>` — Hapus user dari sistem",
        ]

    await event.respond("\n".join(lines))


# ═════════════════════════════════════════════════════════════════════════════
# /status
# ═════════════════════════════════════════════════════════════════════════════

async def cmd_status(event: events.NewMessage.Event) -> None:
    if await _check_blacklist(event):
        return

    user_id = event.sender_id
    row = await db.get_user(user_id)
    level = await db.get_effective_level(user_id)
    level_name = LEVEL_NAMES.get(level, "User")

    if row and row["expires_at"]:
        try:
            expiry = datetime.datetime.fromisoformat(row["expires_at"])
            remaining = expiry - datetime.datetime.now()
            days_left = max(0, remaining.days)
            expiry_str = f"{expiry.strftime('%d-%m-%Y %H:%M')} ({days_left} hari lagi)"
        except ValueError:
            expiry_str = row["expires_at"]
    elif row and row["expires_at"] is None and level > LEVEL_USER:
        expiry_str = "Lifetime ♾️"
    else:
        expiry_str = "—"

    replies = await db.get_autoreplies(user_id)
    bc_basic = await db.get_autobc_messages(user_id, "basic")
    bc_forward = await db.get_autobc_messages(user_id, "forward")
    targets = await db.get_autobc_targets(user_id)

    bc_basic_active = any(r["active"] for r in bc_basic)
    bc_fwd_active = any(r["active"] for r in bc_forward)

    text = (
        "📊 **STATUS AKUN**\n\n"
        f"🆔 User ID: `{user_id}`\n"
        f"👤 Level: **{level_name}**\n"
        f"⏳ Berlaku hingga: {expiry_str}\n\n"
        f"💬 AutoReply rules: {len(replies)}/{AUTOREPLY_MAX_TRIGGERS}\n"
        f"📢 AutoBC Basic: {len(bc_basic)} pesan | "
        f"{'🟢 Aktif' if bc_basic_active else '🔴 Nonaktif'}\n"
        f"📢 AutoBC Forward: {len(bc_forward)} pesan | "
        f"{'🟢 Aktif' if bc_fwd_active else '🔴 Nonaktif'}\n"
        f"🎯 Target BC: {len(targets)} chat"
    )
    await event.respond(text)


# ═════════════════════════════════════════════════════════════════════════════
# Inline button callbacks
# ═════════════════════════════════════════════════════════════════════════════

async def callback_handler(event: events.CallbackQuery.Event) -> None:
    data = event.data.decode()

    if data == "help":
        await event.answer()
        await cmd_help(event)

    elif data == "status":
        await event.answer()
        await cmd_status(event)

    elif data == "terms":
        await event.answer()
        await event.respond(
            "📜 **KETENTUAN PENGGUNAAN**\n\n"
            "✅ Gunakan bot sesuai aturan Telegram\n"
            "❌ Jangan spam atau abuse fitur\n"
            "⏰ Akses Premium aktif sesuai durasi yang dibeli\n"
            "📞 Hubungi Owner/Seller untuk perpanjangan\n"
            "🚫 Pelanggaran = banned permanen"
        )

    elif data == "tutorial":
        await event.answer()
        await event.respond(
            "🎓 **TUTORIAL SINGKAT**\n\n"
            "**AutoReply:**\n"
            "• `/addreply halo | Halo juga! 👋` — Tambah balasan otomatis\n"
            "• `/delreply halo` — Hapus balasan\n\n"
            "**AutoBC:**\n"
            "• `/addbc basic Pesan promo saya!` — Tambah pesan BC\n"
            "• `/addtarget -100123456789` — Tambah target grup\n"
            "• `/setinterval basic 300` — Set interval 5 menit\n"
            "• `/bcstart basic` — Mulai broadcast\n"
            "• `/bcstop basic` — Hentikan broadcast\n\n"
            "**Blacklist (Owner):**\n"
            "• `/addblacklist 123456789 spam` — Blacklist user\n"
            "• `/delblacklist 123456789` — Hapus dari blacklist"
        )

    elif data == "autobc_info":
        await event.answer()
        await event.respond(
            "📢 **AutoBC — Broadcast Otomatis**\n\n"
            "Kirim pesan ke banyak grup/channel secara otomatis.\n\n"
            "Gunakan /help untuk melihat semua perintah AutoBC."
        )

    elif data == "autoreply_info":
        await event.answer()
        await event.respond(
            "💬 **AutoReply — Balas Otomatis**\n\n"
            "Bot akan membalas pesan yang mengandung kata kunci tertentu.\n\n"
            "Gunakan /help untuk melihat semua perintah AutoReply."
        )

    else:
        await event.answer("❓ Tombol tidak dikenal.", alert=True)


# ═════════════════════════════════════════════════════════════════════════════
# AutoReply commands
# ═════════════════════════════════════════════════════════════════════════════

async def cmd_addreply(event: events.NewMessage.Event) -> None:
    if await _check_blacklist(event):
        return
    if not await _require_level(event, LEVEL_PREMIUM):
        return

    try:
        _, rest = event.raw_text.split(None, 1)
        trigger, response = rest.split("|", 1)
        trigger = trigger.strip()
        response = response.strip()
        if not trigger or not response:
            raise ValueError
    except ValueError:
        await event.respond("❌ Format: `/addreply <trigger> | <balasan>`")
        return

    existing = await db.get_autoreplies(event.sender_id)
    if len(existing) >= AUTOREPLY_MAX_TRIGGERS:
        await event.respond(
            f"❌ Batas maksimal {AUTOREPLY_MAX_TRIGGERS} aturan AutoReply tercapai.\n"
            "Hapus beberapa dengan /delreply atau /clearreply."
        )
        return

    await db.add_autoreply(event.sender_id, trigger, response)
    await event.respond(
        f"✅ AutoReply ditambahkan.\n"
        f"🔑 Trigger: `{trigger}`\n"
        f"💬 Balasan: {response}\n"
        f"📊 Total: {len(existing) + 1}/{AUTOREPLY_MAX_TRIGGERS}"
    )


async def cmd_delreply(event: events.NewMessage.Event) -> None:
    if await _check_blacklist(event):
        return
    if not await _require_level(event, LEVEL_PREMIUM):
        return

    try:
        _, trigger = event.raw_text.split(None, 1)
        trigger = trigger.strip()
    except ValueError:
        await event.respond("❌ Format: `/delreply <trigger>`")
        return

    removed = await db.remove_autoreply(event.sender_id, trigger)
    if removed:
        await event.respond(f"✅ AutoReply untuk trigger `{trigger}` dihapus.")
    else:
        await event.respond(f"❌ Trigger `{trigger}` tidak ditemukan.")


async def cmd_clearreply(event: events.NewMessage.Event) -> None:
    if await _check_blacklist(event):
        return
    if not await _require_level(event, LEVEL_PREMIUM):
        return

    count = await db.clear_autoreplies(event.sender_id)
    await event.respond(f"✅ {count} aturan AutoReply dihapus.")


async def cmd_myautoreply(event: events.NewMessage.Event) -> None:
    if await _check_blacklist(event):
        return

    rows = await db.get_autoreplies(event.sender_id)
    if not rows:
        await event.respond("📭 Kamu belum punya aturan AutoReply.")
        return

    lines = ["💬 **DAFTAR AUTOREPLY KAMU**\n"]
    for r in rows:
        lines.append(f"• `{r['trigger']}` → {r['response']}")
    await event.respond("\n".join(lines))


# ── AutoReply listener ────────────────────────────────────────────────────────

async def autoreply_listener(event: events.NewMessage.Event) -> None:
    """
    Passive listener: checks every incoming message against all active
    AutoReply rules stored in the database.
    """
    if event.out:
        return  # Don't reply to our own messages

    sender_id = event.sender_id
    if not sender_id:
        return

    if await db.is_blacklisted(sender_id):
        return

    text = (event.raw_text or "").lower()
    if not text:
        return

    # Collect all users who have AutoReply rules.
    # For each user, check if the message matches any of their triggers.
    # This is intentionally simple — for large deployments a cache would help.
    try:
        # We only reply if the message is in a private chat with the bot owner
        # or in a group where the rule owner is a member.
        # For simplicity: reply in any chat where a trigger matches.
        # The rule owner is identified by the chat context.
        chat_id = event.chat_id

        # Fetch rules for the chat owner (if this is a private chat)
        # or for any user who has rules matching this chat.
        # Simple approach: check rules for the sender's own rules
        # (i.e., the bot replies on behalf of whoever set up the rule).
        # In practice, AutoReply is per-user: each user's rules apply
        # when someone messages THEM (private) or in a group they manage.
        # Here we check rules belonging to the chat_id owner (private chats).
        rules = await db.get_autoreplies(chat_id)  # chat_id == user_id in private
        if not rules:
            return

        for rule in rules:
            if rule["trigger"] in text:
                await event.reply(rule["response"])
                break  # Only one reply per message
    except Exception as exc:
        logger.debug("AutoReply listener error: %s", exc)


# ═════════════════════════════════════════════════════════════════════════════
# AutoBC commands
# ═════════════════════════════════════════════════════════════════════════════

async def cmd_addbc(event: events.NewMessage.Event) -> None:
    if await _check_blacklist(event):
        return
    if not await _require_level(event, LEVEL_PREMIUM):
        return

    try:
        parts = event.raw_text.split(None, 2)
        bc_type = parts[1].lower()
        message = parts[2].strip()
        if bc_type not in ("basic", "forward"):
            raise ValueError
    except (IndexError, ValueError):
        await event.respond("❌ Format: `/addbc basic|forward <pesan>`")
        return

    existing = await db.get_autobc_messages(event.sender_id, bc_type)
    if len(existing) >= AUTOBC_MAX_MESSAGES:
        await event.respond(
            f"❌ Batas maksimal {AUTOBC_MAX_MESSAGES} pesan BC ({bc_type}) tercapai."
        )
        return

    msg_id = await db.add_autobc_message(event.sender_id, bc_type, message)
    await event.respond(
        f"✅ Pesan AutoBC **{bc_type}** ditambahkan (ID: `{msg_id}`).\n"
        f"📊 Total: {len(existing) + 1}/{AUTOBC_MAX_MESSAGES}"
    )


async def cmd_delbc(event: events.NewMessage.Event) -> None:
    if await _check_blacklist(event):
        return
    if not await _require_level(event, LEVEL_PREMIUM):
        return

    try:
        _, msg_id_str = event.raw_text.split(None, 1)
        msg_id = int(msg_id_str.strip())
    except (ValueError, IndexError):
        await event.respond("❌ Format: `/delbc <id>`")
        return

    removed = await db.remove_autobc_message(event.sender_id, msg_id)
    if removed:
        await event.respond(f"✅ Pesan BC ID `{msg_id}` dihapus.")
    else:
        await event.respond(f"❌ Pesan BC ID `{msg_id}` tidak ditemukan.")


async def cmd_setinterval(event: events.NewMessage.Event) -> None:
    if await _check_blacklist(event):
        return
    if not await _require_level(event, LEVEL_PREMIUM):
        return

    try:
        parts = event.raw_text.split()
        bc_type = parts[1].lower()
        interval = int(parts[2])
        if bc_type not in ("basic", "forward") or interval < AUTOBC_MIN_INTERVAL:
            raise ValueError
    except (IndexError, ValueError):
        await event.respond(
            f"❌ Format: `/setinterval basic|forward <detik>`\n"
            f"Minimal interval: {AUTOBC_MIN_INTERVAL} detik."
        )
        return

    await db.set_autobc_interval(event.sender_id, bc_type, interval)
    await event.respond(
        f"✅ Interval AutoBC **{bc_type}** diatur ke **{interval} detik**."
    )


async def cmd_bcstart(event: events.NewMessage.Event, bot: TelegramClient) -> None:
    if await _check_blacklist(event):
        return
    if not await _require_level(event, LEVEL_PREMIUM):
        return

    try:
        _, bc_type = event.raw_text.split(None, 1)
        bc_type = bc_type.strip().lower()
        if bc_type not in ("basic", "forward"):
            raise ValueError
    except ValueError:
        await event.respond("❌ Format: `/bcstart basic|forward`")
        return

    messages = await db.get_autobc_messages(event.sender_id, bc_type)
    if not messages:
        await event.respond(
            f"❌ Tidak ada pesan AutoBC **{bc_type}**. Tambahkan dulu dengan /addbc."
        )
        return

    targets = await db.get_autobc_targets(event.sender_id)
    if not targets:
        await event.respond(
            "❌ Tidak ada target BC. Tambahkan dulu dengan /addtarget."
        )
        return

    await db.set_autobc_active(event.sender_id, bc_type, True)
    key = (event.sender_id, bc_type)

    # Cancel existing task if any
    if key in _bc_tasks and not _bc_tasks[key].done():
        _bc_tasks[key].cancel()

    _bc_tasks[key] = asyncio.create_task(
        _autobc_loop(bot, event.sender_id, bc_type)
    )
    await event.respond(f"🟢 AutoBC **{bc_type}** dimulai.")


async def cmd_bcstop(event: events.NewMessage.Event) -> None:
    if await _check_blacklist(event):
        return
    if not await _require_level(event, LEVEL_PREMIUM):
        return

    try:
        _, bc_type = event.raw_text.split(None, 1)
        bc_type = bc_type.strip().lower()
        if bc_type not in ("basic", "forward"):
            raise ValueError
    except ValueError:
        await event.respond("❌ Format: `/bcstop basic|forward`")
        return

    await db.set_autobc_active(event.sender_id, bc_type, False)
    key = (event.sender_id, bc_type)
    if key in _bc_tasks and not _bc_tasks[key].done():
        _bc_tasks[key].cancel()
        del _bc_tasks[key]

    await event.respond(f"🔴 AutoBC **{bc_type}** dihentikan.")


async def cmd_myautobc(event: events.NewMessage.Event) -> None:
    if await _check_blacklist(event):
        return

    basic = await db.get_autobc_messages(event.sender_id, "basic")
    forward = await db.get_autobc_messages(event.sender_id, "forward")
    targets = await db.get_autobc_targets(event.sender_id)

    lines = ["📢 **DAFTAR AUTOBC KAMU**\n"]

    lines.append("**Basic:**")
    if basic:
        for r in basic:
            status = "🟢" if r["active"] else "🔴"
            lines.append(
                f"  {status} ID `{r['id']}` | interval {r['interval_sec']}s\n"
                f"     _{r['message'][:60]}{'…' if len(r['message']) > 60 else ''}_"
            )
    else:
        lines.append("  (kosong)")

    lines.append("\n**Forward:**")
    if forward:
        for r in forward:
            status = "🟢" if r["active"] else "🔴"
            lines.append(
                f"  {status} ID `{r['id']}` | interval {r['interval_sec']}s\n"
                f"     _{r['message'][:60]}{'…' if len(r['message']) > 60 else ''}_"
            )
    else:
        lines.append("  (kosong)")

    lines.append(f"\n🎯 **Target:** {len(targets)} chat")
    if targets:
        for t in targets:
            lines.append(f"  • `{t['chat_id']}`")

    await event.respond("\n".join(lines))


async def cmd_addtarget(event: events.NewMessage.Event) -> None:
    if await _check_blacklist(event):
        return
    if not await _require_level(event, LEVEL_PREMIUM):
        return

    try:
        _, chat_id_str = event.raw_text.split(None, 1)
        chat_id = int(chat_id_str.strip())
    except (ValueError, IndexError):
        await event.respond("❌ Format: `/addtarget <chat_id>`")
        return

    await db.add_autobc_target(event.sender_id, chat_id)
    await event.respond(f"✅ Target `{chat_id}` ditambahkan ke daftar BC.")


async def cmd_deltarget(event: events.NewMessage.Event) -> None:
    if await _check_blacklist(event):
        return
    if not await _require_level(event, LEVEL_PREMIUM):
        return

    try:
        _, chat_id_str = event.raw_text.split(None, 1)
        chat_id = int(chat_id_str.strip())
    except (ValueError, IndexError):
        await event.respond("❌ Format: `/deltarget <chat_id>`")
        return

    removed = await db.remove_autobc_target(event.sender_id, chat_id)
    if removed:
        await event.respond(f"✅ Target `{chat_id}` dihapus dari daftar BC.")
    else:
        await event.respond(f"❌ Target `{chat_id}` tidak ditemukan.")


# ── AutoBC background loop ────────────────────────────────────────────────────

async def _autobc_loop(bot: TelegramClient, owner_id: int, bc_type: str) -> None:
    """
    Continuously broadcast messages to all registered targets.
    Runs until cancelled or the active flag is cleared in the DB.
    """
    logger.info("AutoBC loop started: owner=%s type=%s", owner_id, bc_type)
    msg_index = 0

    try:
        while True:
            messages = await db.get_autobc_messages(owner_id, bc_type)
            active_msgs = [m for m in messages if m["active"]]

            if not active_msgs:
                logger.info("AutoBC loop: no active messages, stopping.")
                break

            targets = await db.get_autobc_targets(owner_id)
            if not targets:
                await asyncio.sleep(60)
                continue

            msg = active_msgs[msg_index % len(active_msgs)]
            interval = msg["interval_sec"]
            msg_index += 1

            for target in targets:
                try:
                    await bot.send_message(target["chat_id"], msg["message"])
                    await asyncio.sleep(2)  # Small delay between sends
                except FloodWaitError as e:
                    logger.warning("FloodWait %ss during AutoBC", e.seconds)
                    await asyncio.sleep(e.seconds)
                except Exception as exc:
                    logger.warning("AutoBC send error to %s: %s", target["chat_id"], exc)

            await asyncio.sleep(interval)

    except asyncio.CancelledError:
        logger.info("AutoBC loop cancelled: owner=%s type=%s", owner_id, bc_type)
    except Exception as exc:
        logger.error("AutoBC loop crashed: %s", exc, exc_info=True)


# ═════════════════════════════════════════════════════════════════════════════
# Blacklist commands (Owner only)
# ═════════════════════════════════════════════════════════════════════════════

async def cmd_addblacklist(event: events.NewMessage.Event) -> None:
    if not await _require_level(event, LEVEL_OWNER):
        return

    try:
        parts = event.raw_text.split(None, 2)
        target_id = int(parts[1])
        reason = parts[2].strip() if len(parts) > 2 else None
    except (IndexError, ValueError):
        await event.respond("❌ Format: `/addblacklist <user_id> [alasan]`")
        return

    if target_id == OWNER_ID:
        await event.respond("❌ Tidak bisa memblacklist Owner.")
        return

    await db.add_blacklist(target_id, reason)
    reason_str = f"\n📝 Alasan: {reason}" if reason else ""
    await event.respond(f"✅ User `{target_id}` diblacklist.{reason_str}")


async def cmd_delblacklist(event: events.NewMessage.Event) -> None:
    if not await _require_level(event, LEVEL_OWNER):
        return

    try:
        _, target_id_str = event.raw_text.split(None, 1)
        target_id = int(target_id_str.strip())
    except (ValueError, IndexError):
        await event.respond("❌ Format: `/delblacklist <user_id>`")
        return

    await db.remove_blacklist(target_id)
    await event.respond(f"✅ User `{target_id}` dihapus dari blacklist.")


async def cmd_listblacklist(event: events.NewMessage.Event) -> None:
    if not await _require_level(event, LEVEL_OWNER):
        return

    rows = await db.get_blacklist()
    if not rows:
        await event.respond("📭 Blacklist kosong.")
        return

    lines = [f"🚫 **BLACKLIST** ({len(rows)} user)\n"]
    for r in rows:
        reason_str = f" — {r['reason']}" if r["reason"] else ""
        lines.append(f"• `{r['user_id']}`{reason_str}")
    await event.respond("\n".join(lines))


# ═════════════════════════════════════════════════════════════════════════════
# User management commands
# ═════════════════════════════════════════════════════════════════════════════

async def cmd_addseller(event: events.NewMessage.Event) -> None:
    if not await _require_level(event, LEVEL_OWNER):
        return

    try:
        _, uid_str = event.raw_text.split(None, 1)
        uid = int(uid_str.strip())
    except (ValueError, IndexError):
        await event.respond("❌ Format: `/addseller <user_id>`")
        return

    await db.upsert_user(uid, LEVEL_SELLER, None)
    await event.respond(f"✅ User `{uid}` dijadikan **Seller 💼**.")


async def cmd_delseller(event: events.NewMessage.Event) -> None:
    if not await _require_level(event, LEVEL_OWNER):
        return

    try:
        _, uid_str = event.raw_text.split(None, 1)
        uid = int(uid_str.strip())
    except (ValueError, IndexError):
        await event.respond("❌ Format: `/delseller <user_id>`")
        return

    await db.upsert_user(uid, LEVEL_USER, None)
    await event.respond(f"✅ Seller `{uid}` diturunkan ke User.")


async def cmd_addprem(event: events.NewMessage.Event) -> None:
    if not await _require_level(event, LEVEL_SELLER):
        return

    try:
        parts = event.raw_text.split()
        if len(parts) < 3:
            raise ValueError

        duration_str = parts[-1].lower()
        user_ids = [int(x) for x in parts[1:-1]]

        if duration_str == "lifetime":
            expires_at = None  # NULL = lifetime
        else:
            days = int(duration_str)
            if days < 1:
                raise ValueError
            expiry = datetime.datetime.now() + datetime.timedelta(days=days)
            expires_at = expiry.isoformat()

    except (ValueError, IndexError):
        await event.respond(
            "❌ Format: `/addprem <user_id1> [user_id2 ...] <hari|lifetime>`"
        )
        return

    for uid in user_ids:
        await db.upsert_user(uid, LEVEL_PREMIUM, expires_at)

    if expires_at is None:
        expiry_label = "Lifetime ♾️"
    else:
        expiry_label = datetime.datetime.fromisoformat(expires_at).strftime(
            "%d-%m-%Y %H:%M"
        )

    await event.respond(
        f"✅ Premium diberikan ke **{len(user_ids)} user**.\n"
        f"⏳ Berlaku hingga: {expiry_label}"
    )


async def cmd_delprem(event: events.NewMessage.Event) -> None:
    if not await _require_level(event, LEVEL_OWNER):
        return

    try:
        _, uid_str = event.raw_text.split(None, 1)
        uid = int(uid_str.strip())
    except (ValueError, IndexError):
        await event.respond("❌ Format: `/delprem <user_id>`")
        return

    await db.upsert_user(uid, LEVEL_USER, None)
    await event.respond(f"✅ Premium user `{uid}` dicabut.")


async def cmd_deluser(event: events.NewMessage.Event) -> None:
    if not await _require_level(event, LEVEL_OWNER):
        return

    try:
        _, uid_str = event.raw_text.split(None, 1)
        uid = int(uid_str.strip())
    except (ValueError, IndexError):
        await event.respond("❌ Format: `/deluser <user_id>`")
        return

    if uid == OWNER_ID:
        await event.respond("❌ Tidak bisa menghapus Owner.")
        return

    await db.remove_user(uid)
    await event.respond(f"✅ User `{uid}` dihapus dari sistem.")


async def cmd_listusers(event: events.NewMessage.Event) -> None:
    if not await _require_level(event, LEVEL_OWNER):
        return

    rows = await db.get_all_users()
    if not rows:
        await event.respond("📭 Tidak ada user terdaftar.")
        return

    lines = [f"👥 **DAFTAR USER** ({len(rows)} total)\n"]
    for r in rows:
        level_name = LEVEL_NAMES.get(r["level"], "?")
        expires = r["expires_at"] or "Lifetime"
        lines.append(f"• `{r['user_id']}` — {level_name} | {expires}")

    # Split into chunks to avoid message length limits
    chunk: list[str] = []
    for line in lines:
        chunk.append(line)
        if len("\n".join(chunk)) > 3500:
            await event.respond("\n".join(chunk))
            chunk = []
    if chunk:
        await event.respond("\n".join(chunk))


# ═════════════════════════════════════════════════════════════════════════════
# Owner broadcast
# ═════════════════════════════════════════════════════════════════════════════

async def cmd_broadcast(event: events.NewMessage.Event, bot: TelegramClient) -> None:
    if not await _require_level(event, LEVEL_OWNER):
        return

    try:
        _, message = event.raw_text.split(None, 1)
        message = message.strip()
    except ValueError:
        await event.respond("❌ Format: `/broadcast <pesan>`")
        return

    users = await db.get_all_users()
    sent = 0
    failed = 0

    status_msg = await event.respond(
        f"📤 Mengirim broadcast ke {len(users)} user..."
    )

    for user in users:
        uid = user["user_id"]
        if uid == event.sender_id:
            continue
        try:
            await bot.send_message(uid, f"📢 **BROADCAST**\n\n{message}")
            sent += 1
            await asyncio.sleep(0.5)
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except (UserPrivacyRestrictedError, Exception):
            failed += 1

    await status_msg.edit(
        f"✅ Broadcast selesai.\n"
        f"📨 Terkirim: {sent}\n"
        f"❌ Gagal: {failed}"
    )


# ═════════════════════════════════════════════════════════════════════════════
# Handler registration
# ═════════════════════════════════════════════════════════════════════════════

def register_handlers(bot: TelegramClient) -> None:
    """Attach all event handlers to the bot client."""

    # ── Commands ──────────────────────────────────────────────────────────────
    bot.add_event_handler(cmd_start, events.NewMessage(pattern=r"^/start(?:\s|$)"))
    bot.add_event_handler(cmd_help, events.NewMessage(pattern=r"^/help(?:\s|$)"))
    bot.add_event_handler(cmd_status, events.NewMessage(pattern=r"^/status(?:\s|$)"))

    # AutoReply
    bot.add_event_handler(cmd_addreply, events.NewMessage(pattern=r"^/addreply(?:\s|$)"))
    bot.add_event_handler(cmd_delreply, events.NewMessage(pattern=r"^/delreply(?:\s|$)"))
    bot.add_event_handler(cmd_clearreply, events.NewMessage(pattern=r"^/clearreply(?:\s|$)"))
    bot.add_event_handler(cmd_myautoreply, events.NewMessage(pattern=r"^/myautoreply(?:\s|$)"))

    # AutoBC
    bot.add_event_handler(cmd_addbc, events.NewMessage(pattern=r"^/addbc(?:\s|$)"))
    bot.add_event_handler(cmd_delbc, events.NewMessage(pattern=r"^/delbc(?:\s|$)"))
    bot.add_event_handler(cmd_setinterval, events.NewMessage(pattern=r"^/setinterval(?:\s|$)"))
    bot.add_event_handler(cmd_myautobc, events.NewMessage(pattern=r"^/myautobc(?:\s|$)"))
    bot.add_event_handler(cmd_addtarget, events.NewMessage(pattern=r"^/addtarget(?:\s|$)"))
    bot.add_event_handler(cmd_deltarget, events.NewMessage(pattern=r"^/deltarget(?:\s|$)"))

    # bcstart / bcstop need the bot client injected
    async def _bcstart(event):
        await cmd_bcstart(event, bot)

    async def _bcstop(event):
        await cmd_bcstop(event)

    bot.add_event_handler(_bcstart, events.NewMessage(pattern=r"^/bcstart(?:\s|$)"))
    bot.add_event_handler(_bcstop, events.NewMessage(pattern=r"^/bcstop(?:\s|$)"))

    # Blacklist
    bot.add_event_handler(cmd_addblacklist, events.NewMessage(pattern=r"^/addblacklist(?:\s|$)"))
    bot.add_event_handler(cmd_delblacklist, events.NewMessage(pattern=r"^/delblacklist(?:\s|$)"))
    bot.add_event_handler(cmd_listblacklist, events.NewMessage(pattern=r"^/listblacklist(?:\s|$)"))

    # User management
    bot.add_event_handler(cmd_addseller, events.NewMessage(pattern=r"^/addseller(?:\s|$)"))
    bot.add_event_handler(cmd_delseller, events.NewMessage(pattern=r"^/delseller(?:\s|$)"))
    bot.add_event_handler(cmd_addprem, events.NewMessage(pattern=r"^/addprem(?:\s|$)"))
    bot.add_event_handler(cmd_delprem, events.NewMessage(pattern=r"^/delprem(?:\s|$)"))
    bot.add_event_handler(cmd_deluser, events.NewMessage(pattern=r"^/deluser(?:\s|$)"))
    bot.add_event_handler(cmd_listusers, events.NewMessage(pattern=r"^/listusers(?:\s|$)"))

    # Broadcast
    async def _broadcast(event):
        await cmd_broadcast(event, bot)

    bot.add_event_handler(_broadcast, events.NewMessage(pattern=r"^/broadcast(?:\s|$)"))

    # ── Inline button callbacks ───────────────────────────────────────────────
    bot.add_event_handler(callback_handler, events.CallbackQuery())

    # ── Passive AutoReply listener (lowest priority — catches all messages) ───
    bot.add_event_handler(autoreply_listener, events.NewMessage(incoming=True))

    logger.info("All handlers registered.")


# ═════════════════════════════════════════════════════════════════════════════
# Restore active AutoBC tasks on startup
# ═════════════════════════════════════════════════════════════════════════════

async def restore_autobc_tasks(bot: TelegramClient) -> None:
    """
    Re-launch AutoBC background tasks for any rows that were active
    when the bot last shut down.
    """
    rows = await db.get_active_autobc()
    seen: set[tuple[int, str]] = set()

    for row in rows:
        key = (row["owner_id"], row["bc_type"])
        if key in seen:
            continue
        seen.add(key)

        targets = await db.get_autobc_targets(row["owner_id"])
        if not targets:
            continue

        logger.info(
            "Restoring AutoBC task: owner=%s type=%s",
            row["owner_id"],
            row["bc_type"],
        )
        _bc_tasks[key] = asyncio.create_task(
            _autobc_loop(bot, row["owner_id"], row["bc_type"])
        )

    if seen:
        logger.info("Restored %d AutoBC task(s).", len(seen))
