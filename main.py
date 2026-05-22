import os

from pyrogram import Client, filters

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client(
    "StoreBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start(client, message):

    await message.reply_text(
        "BOT HIDUP"
    )

@app.on_message(filters.command("ping"))
async def ping(client, message):

    print("PING MASUK")

    await message.reply_text(
        "PONG"
    )

print("🚀 BOT ONLINE")

app.run()
