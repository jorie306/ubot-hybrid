import sqlite3
import os

OWNER_ID = int(os.getenv("OWNER_ID"))

db = sqlite3.connect(
    "storebot.db",
    check_same_thread=False
)

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    role TEXT DEFAULT 'FREE'
)
""")

db.commit()

ROLES = {
    "OWNER": 4,
    "ADMIN": 3,
    "SELLER": 2,
    "PREM": 1,
    "FREE": 0
}

def get_role(user_id):

    if user_id == OWNER_ID:
        return "OWNER"

    cursor.execute(
        "SELECT role FROM users WHERE user_id=?",
        (user_id,)
    )

    data = cursor.fetchone()

    if data:
        return data[0]

    return "FREE"

def set_role(user_id, role):

    cursor.execute(
        "INSERT OR REPLACE INTO users(user_id, role) VALUES(?, ?)",
        (user_id, role)
    )

    db.commit()

def has_access(user_id, role):

    return ROLES.get(
        get_role(user_id),
        0
    ) >= ROLES.get(role, 0)
