import os
import logging
import subprocess
import json
from pymongo import MongoClient
from pyrogram import *
from pyrogram.types import *
from pyrogram.errors.exceptions.bad_request_400 import ButtonDataInvalid
import asyncio

# ---------------- LOGGING ----------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# ---------------- BOT INIT ----------------
app = Client("hanime", bot_token="", api_id=6, api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e")



# ---------------- COMMAND: START ----------------
@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text(
        "**Welcome!**\n"
        "`/search <query>` — Search HAnime\n"
        "`/download <hanime.tv URL>` — Download directly"
        "`/playlist <hanime.tv playlist URL>` — Download all playlists directly"
    )


@app.on_message(filters.command("search"))
async def search_cmd(_, msg):
    query = " ".join(msg.command[1:])
    if not query:
        await msg.reply_text("Usage: `/search <keywords>`", parse_mode="markdown")
        return

    proc = subprocess.run(["htv-search", "-q", query], capture_output=True, text=True)
    stdout = proc.stdout.strip()
    if not stdout:
        await msg.reply_text("No results found.")
        return

    # Plain text listing
    response = "Search results:\n\n" + stdout
    await msg.reply_text(response)

@app.on_message(filters.command("download"))
async def download_cmd(_, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: `/download <hanime.tv video URL>`", parse_mode="markdown")
        return

    url = message.command[1]
    chat_id = message.chat.id

    await message.reply_text("Downloading (MP4)... This may take a while ⏳")

    subprocess.run([
        "yt-dlp",
        "-f", "mp4",
        "-o", "%(title)s.%(ext)s",
        url
    ], capture_output=True, text=True)

    mp4_files = [
        f for f in os.listdir() if os.path.isfile(f)
        and f.lower().endswith(".mp4") and not f.endswith(".part")
    ]

    if not mp4_files:
        await message.reply_text("Download failed or no MP4 file found.")
        return

    file_path = mp4_files[0]
    await message.reply_text("Uploading the MP4 now…")

    await app.send_video(chat_id, file_path, caption="Here’s your video (MP4)")

    os.remove(file_path)
    await message.reply_text("Done! File sent successfully.")

@app.on_message(filters.command("playlist"))
async def download_cmd(_, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: `/playlist <hanime.tv playlist URL only>`")
        return

    url = message.command[1]
    chat_id = message.chat.id

    await message.reply_text("Downloading (MP4)... This may take a while ⏳")

    subprocess.run([
        "yt-dlp",
        "-f", "mp4",
        "-o", "%(title)s.%(ext)s",
        url
    ], capture_output=True, text=True)

    mp4_files = [
        f for f in os.listdir() if os.path.isfile(f)
        and f.lower().endswith(".mp4") and not f.endswith(".part")
    ]

    if not mp4_files:
        await message.reply_text("Download failed or no MP4 file found.")
        return


    for file in mp4_files:
        await asyncio.sleep(0.5)
        await app.send_video(message.chat.id, file, caption=f"{file}")
        os.remove(file)

    await message.reply_text("All playlist videos sent! 🎉")


app.start()
idle()
