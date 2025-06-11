import os
import re
import json
import psutil
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from subprocess import run, PIPE

API_ID = 123456  # 🔁 Replace with your API ID
API_HASH = "your_api_hash"  # 🔁 Replace with your API HASH
BOT_TOKEN = "your_bot_token"  # 🔁 Replace with your BOT TOKEN

OWNER_ID = 7447651332
ALLOWED_CHAT_ID = -1002432150473
AUTH_FILE = "authorized_users.json"

# Load authorized users
if os.path.exists(AUTH_FILE):
    with open(AUTH_FILE, "r") as f:
        AUTH_USERS = set(json.load(f))
else:
    AUTH_USERS = {OWNER_ID}
    with open(AUTH_FILE, "w") as f:
        json.dump(list(AUTH_USERS), f)

def save_auth_users():
    with open(AUTH_FILE, "w") as f:
        json.dump(list(AUTH_USERS), f)

app = Client("vj_m3u8_leech_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

M3U8_REGEX = r'https:\/\/.*\.m3u8'

def download_m3u8(url: str, output: str):
    command = [
        "ffmpeg", "-i", url,
        "-c", "copy", "-bsf:a", "aac_adtstoasc",
        output
    ]
    result = run(command, stdout=PIPE, stderr=PIPE)
    return result.returncode == 0

async def simulate_progress(msg, file_name, user):
    for i in range(0, 101, 10):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        bar = "⬡" * (i // 10) + "▫" * ((100 - i) // 10)
        text = f"""1. {file_name} ( FR4 )

Task By {user.first_name}  ( #{user.id} ) [Link]
┟ [{bar}] {i}%
┠ Processed → {i}MB of 100MB
┠ Status → Downloading
┠ Speed → 2MB/s
┠ Time → {i}s of 100s ( {100-i}s left )
┠ Engine → sonic
┠ In Mode → #ytdlp
┠ Out Mode → #Leech
┖ Stop → /c_{msg.id}

⌬ Bot Stats
┟ CPU → {cpu}% | F → 158.14GB [82.1%]
┖ RAM → {ram}% | UP → 6d18h15m31s
"""  
        await msg.edit(text)
        await asyncio.sleep(1)

@app.on_message(filters.command("add") & filters.user(OWNER_ID))
async def add_user(client: Client, message: Message):
    if len(message.command) < 2 or not message.command[1].isdigit():
        return await message.reply("Usage: /add <user_id>")
    user_id = int(message.command[1])
    AUTH_USERS.add(user_id)
    save_auth_users()
    await message.reply(f"✅ User {user_id} authorized.")

@app.on_message(filters.command("XD"))
async def xd_command(client: Client, message: Message):
    if message.chat.type == "private":
        return await message.reply("❌ Bot can only be used in the group.")

    if message.chat.id != ALLOWED_CHAT_ID:
        return await message.reply("❌ Bot is not allowed in this group.")    

    if message.from_user.id not in AUTH_USERS:
        return await message.reply("❌ You are not authorized to use this bot.")

    if len(message.command) < 2:
        return await message.reply("Usage: /XD <.m3u8 URL>")

    url = message.command[1]
    if re.search(M3U8_REGEX, url):
        output_name = f"{message.from_user.id}_video.mp4"
        status = await message.reply("🔄 Starting download...")
        await simulate_progress(status, "neev", message.from_user)
        if download_m3u8(url, output_name):
            await client.send_video(OWNER_ID, output_name, caption="✅ Download complete!")
            os.remove(output_name)
        else:
            await message.reply("❌ Download failed. Invalid or expired URL.")
    else:
        await message.reply("Please send a valid .m3u8 URL.")

app.run()
