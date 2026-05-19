"""
database.py — SQLite persistence layer.

All blocking sqlite3 calls are wrapped with asyncio.to_thread so they
never stall the Telethon event loop.
"""

import asyncio
import datetime
import logging
import sqlite3
from contextlib import contextmanager
from typing import Optional

from config import DB_PATH, LEVEL_OWNER, LEVEL_USER, OWNER_ID

logger = logging.getLogger(__name__)


# ── Connection helper ─────────────────────────────────────────────────────────

@contextmanager
def _get_conn():
    """Yield a sqlite3 connection with WAL mode and foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Schema initialisation ─────────────────────────────────────────────────────

def _init_db_sync() -> None:
    """Create all tables if they do not exist and seed the owner row."""
    with _get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                level       INTEGER NOT NULL DEFAULT 0,
                expires_at  TEXT,           -- ISO-8601 or NULL (= lifetime)
                created_at  TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS blacklist (
                user_id     INTEGER PRIMARY KEY,
                reason      TEXT,
                created_at  TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS autoreply (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id    INTEGER NOT NULL,
                trigger     TEXT NOT NULL,
                response    TEXT NOT NULL,
                created_at  TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(owner_id, trigger)
            );

            CREATE TABLE IF NOT EXISTS autobc (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id     INTEGER NOT NULL,
                bc_type      TEXT NOT NULL DEFAULT 'basic',  -- 'basic' | 'forward'
                message      TEXT NOT NULL,
                interval_sec INTEGER NOT NULL DEFAULT 180,
                active       INTEGER NOT NULL DEFAULT 0,     -- 0 | 1
                created_at   TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS autobc_targets (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id    INTEGER NOT NULL,
                chat_id     INTEGER NOT NULL,
                UNIQUE(owner_id, chat_id)
            );
        """)

        # Ensure the owner always exists in the users table.
        if OWNER_ID:
            conn.execute(
                "INSERT OR IGNORE INTO users (user_id, level) VALUES (?, ?)",
                (OWNER_ID, LEVEL_OWNER),
            )

    logger.info("Database initialised at %s", DB_PATH)


async def init_db() -> None:
    await asyncio.to_thread(_init_db_sync)


# ── User / access-level helpers ───────────────────────────────────────────────

def _get_user_sync(user_id: int) -> Optional[sqlite3.Row]:
    with _get_conn() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()


async def get_user(user_id: int) -> Optional[sqlite3.Row]:
    return await asyncio.to_thread(_get_user_sync, user_id)


def _upsert_user_sync(user_id: int, level: int, expires_at: Optional[str]) -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO users (user_id, level, expires_at)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                level      = excluded.level,
                expires_at = excluded.expires_at
            """,
            (user_id, level, expires_at),
        )


async def upsert_user(user_id: int, level: int, expires_at: Optional[str] = None) -> None:
    await asyncio.to_thread(_upsert_user_sync, user_id, level, expires_at)


def _remove_user_sync(user_id: int) -> None:
    with _get_conn() as conn:
        conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))


async def remove_user(user_id: int) -> None:
    await asyncio.to_thread(_remove_user_sync, user_id)


def _get_all_users_sync() -> list[sqlite3.Row]:
    with _get_conn() as conn:
        return conn.execute(
            "SELECT * FROM users ORDER BY level DESC, user_id"
        ).fetchall()


async def get_all_users() -> list[sqlite3.Row]:
    return await asyncio.to_thread(_get_all_users_sync)


def _get_effective_level_sync(user_id: int) -> int:
    """
    Return the effective access level for a user.
    Expired premium/seller accounts fall back to LEVEL_USER.
    """
    if user_id == OWNER_ID:
        return LEVEL_OWNER

    with _get_conn() as conn:
        row = conn.execute(
            "SELECT level, expires_at FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()

    if row is None:
        return LEVEL_USER

    level: int = row["level"]
    expires_at: Optional[str] = row["expires_at"]

    if level == LEVEL_OWNER:
        return LEVEL_OWNER

    # NULL expires_at means lifetime.
    if expires_at is None:
        return level

    try:
        expiry = datetime.datetime.fromisoformat(expires_at)
        if datetime.datetime.now() > expiry:
            return LEVEL_USER
    except ValueError:
        pass

    return level


async def get_effective_level(user_id: int) -> int:
    return await asyncio.to_thread(_get_effective_level_sync, user_id)


# ── Blacklist helpers ─────────────────────────────────────────────────────────

def _add_blacklist_sync(user_id: int, reason: Optional[str] = None) -> None:
    with _get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO blacklist (user_id, reason) VALUES (?, ?)",
            (user_id, reason),
        )


async def add_blacklist(user_id: int, reason: Optional[str] = None) -> None:
    await asyncio.to_thread(_add_blacklist_sync, user_id, reason)


def _remove_blacklist_sync(user_id: int) -> None:
    with _get_conn() as conn:
        conn.execute("DELETE FROM blacklist WHERE user_id = ?", (user_id,))


async def remove_blacklist(user_id: int) -> None:
    await asyncio.to_thread(_remove_blacklist_sync, user_id)


def _is_blacklisted_sync(user_id: int) -> bool:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM blacklist WHERE user_id = ?", (user_id,)
        ).fetchone()
    return row is not None


async def is_blacklisted(user_id: int) -> bool:
    return await asyncio.to_thread(_is_blacklisted_sync, user_id)


def _get_blacklist_sync() -> list[sqlite3.Row]:
    with _get_conn() as conn:
        return conn.execute("SELECT * FROM blacklist ORDER BY created_at DESC").fetchall()


async def get_blacklist() -> list[sqlite3.Row]:
    return await asyncio.to_thread(_get_blacklist_sync)


# ── AutoReply helpers ─────────────────────────────────────────────────────────

def _add_autoreply_sync(owner_id: int, trigger: str, response: str) -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO autoreply (owner_id, trigger, response)
            VALUES (?, ?, ?)
            ON CONFLICT(owner_id, trigger) DO UPDATE SET response = excluded.response
            """,
            (owner_id, trigger.lower().strip(), response),
        )


async def add_autoreply(owner_id: int, trigger: str, response: str) -> None:
    await asyncio.to_thread(_add_autoreply_sync, owner_id, trigger, response)


def _remove_autoreply_sync(owner_id: int, trigger: str) -> bool:
    with _get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM autoreply WHERE owner_id = ? AND trigger = ?",
            (owner_id, trigger.lower().strip()),
        )
    return cur.rowcount > 0


async def remove_autoreply(owner_id: int, trigger: str) -> bool:
    return await asyncio.to_thread(_remove_autoreply_sync, owner_id, trigger)


def _get_autoreplies_sync(owner_id: int) -> list[sqlite3.Row]:
    with _get_conn() as conn:
        return conn.execute(
            "SELECT * FROM autoreply WHERE owner_id = ? ORDER BY trigger",
            (owner_id,),
        ).fetchall()


async def get_autoreplies(owner_id: int) -> list[sqlite3.Row]:
    return await asyncio.to_thread(_get_autoreplies_sync, owner_id)


def _clear_autoreplies_sync(owner_id: int) -> int:
    with _get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM autoreply WHERE owner_id = ?", (owner_id,)
        )
    return cur.rowcount


async def clear_autoreplies(owner_id: int) -> int:
    return await asyncio.to_thread(_clear_autoreplies_sync, owner_id)


# ── AutoBC helpers ────────────────────────────────────────────────────────────

def _add_autobc_message_sync(
    owner_id: int, bc_type: str, message: str, interval_sec: int
) -> int:
    with _get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO autobc (owner_id, bc_type, message, interval_sec)
            VALUES (?, ?, ?, ?)
            """,
            (owner_id, bc_type, message, interval_sec),
        )
    return cur.lastrowid


async def add_autobc_message(
    owner_id: int, bc_type: str, message: str, interval_sec: int = 180
) -> int:
    return await asyncio.to_thread(
        _add_autobc_message_sync, owner_id, bc_type, message, interval_sec
    )


def _remove_autobc_message_sync(owner_id: int, msg_id: int) -> bool:
    with _get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM autobc WHERE id = ? AND owner_id = ?", (msg_id, owner_id)
        )
    return cur.rowcount > 0


async def remove_autobc_message(owner_id: int, msg_id: int) -> bool:
    return await asyncio.to_thread(_remove_autobc_message_sync, owner_id, msg_id)


def _get_autobc_messages_sync(owner_id: int, bc_type: str) -> list[sqlite3.Row]:
    with _get_conn() as conn:
        return conn.execute(
            "SELECT * FROM autobc WHERE owner_id = ? AND bc_type = ? ORDER BY id",
            (owner_id, bc_type),
        ).fetchall()


async def get_autobc_messages(owner_id: int, bc_type: str) -> list[sqlite3.Row]:
    return await asyncio.to_thread(_get_autobc_messages_sync, owner_id, bc_type)


def _set_autobc_active_sync(owner_id: int, bc_type: str, active: bool) -> None:
    with _get_conn() as conn:
        conn.execute(
            "UPDATE autobc SET active = ? WHERE owner_id = ? AND bc_type = ?",
            (1 if active else 0, owner_id, bc_type),
        )


async def set_autobc_active(owner_id: int, bc_type: str, active: bool) -> None:
    await asyncio.to_thread(_set_autobc_active_sync, owner_id, bc_type, active)


def _set_autobc_interval_sync(owner_id: int, bc_type: str, interval_sec: int) -> None:
    with _get_conn() as conn:
        conn.execute(
            "UPDATE autobc SET interval_sec = ? WHERE owner_id = ? AND bc_type = ?",
            (interval_sec, owner_id, bc_type),
        )


async def set_autobc_interval(owner_id: int, bc_type: str, interval_sec: int) -> None:
    await asyncio.to_thread(_set_autobc_interval_sync, owner_id, bc_type, interval_sec)


def _get_active_autobc_sync() -> list[sqlite3.Row]:
    """Return all active AutoBC rows (used by the broadcast loop)."""
    with _get_conn() as conn:
        return conn.execute(
            "SELECT * FROM autobc WHERE active = 1 ORDER BY owner_id, bc_type, id"
        ).fetchall()


async def get_active_autobc() -> list[sqlite3.Row]:
    return await asyncio.to_thread(_get_active_autobc_sync)


def _clear_autobc_sync(owner_id: int, bc_type: str) -> int:
    with _get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM autobc WHERE owner_id = ? AND bc_type = ?",
            (owner_id, bc_type),
        )
    return cur.rowcount


async def clear_autobc(owner_id: int, bc_type: str) -> int:
    return await asyncio.to_thread(_clear_autobc_sync, owner_id, bc_type)


# ── AutoBC target helpers ─────────────────────────────────────────────────────

def _add_autobc_target_sync(owner_id: int, chat_id: int) -> None:
    with _get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO autobc_targets (owner_id, chat_id) VALUES (?, ?)",
            (owner_id, chat_id),
        )


async def add_autobc_target(owner_id: int, chat_id: int) -> None:
    await asyncio.to_thread(_add_autobc_target_sync, owner_id, chat_id)


def _remove_autobc_target_sync(owner_id: int, chat_id: int) -> bool:
    with _get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM autobc_targets WHERE owner_id = ? AND chat_id = ?",
            (owner_id, chat_id),
        )
    return cur.rowcount > 0


async def remove_autobc_target(owner_id: int, chat_id: int) -> bool:
    return await asyncio.to_thread(_remove_autobc_target_sync, owner_id, chat_id)


def _get_autobc_targets_sync(owner_id: int) -> list[sqlite3.Row]:
    with _get_conn() as conn:
        return conn.execute(
            "SELECT chat_id FROM autobc_targets WHERE owner_id = ?", (owner_id,)
        ).fetchall()


async def get_autobc_targets(owner_id: int) -> list[sqlite3.Row]:
    return await asyncio.to_thread(_get_autobc_targets_sync, owner_id)
