import os
import logging
import subprocess
import json
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


def link_fil(filter, client, message):
    if "hanime.tv/videos" in message.text:
        return True
    else:
        return False

link_filter = filters.create(link_fil, name="link_filter")


# ---------------- COMMAND: START ----------------
@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text(
        "**Welcome!**\n"
        "`/search <query>` — Search HAnime\n"
        "`/download <hanime.tv URL>` — Download directly"
        "`/playlist <hanime.tv playlist URL>` — Download all playlists directly"
    )

# ---------------- COMMAND: SEARCH ----------------

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



# ------------- DOWNLOAD COMMAND -------------
@app.on_message(link_filter)
async def download_cmd(_, message):
        print(message.text)
        await message.reply("Download?", 
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Yep", f"d_{message.text}"), InlineKeyboardButton("Nah", callback_data="delete_")]
            ])
            )


@app.on_callback_query(filters.regex("delete_"))
async def del_callback(_, callback: CallbackQuery):  
  await callback.message.edit("Ok")   

@app.on_callback_query(filters.regex("^d"))
async def download_video(client, callback : CallbackQuery):
    url = callback.data.split("_",1)[1]
    msg = await callback.message.edit("Downloading (MP4)... This may take a while ⏳")
    user_id = callback.message.from_user.id
    # Ensure MP4 format using yt-dlp
    subprocess.run([
        "yt-dlp",
        "-f", "mp4",
        "-o", "%(title)s.%(ext)s",
        url
    ], capture_output=True, text=True)


    for file in os.listdir('.'):
        if file.endswith(".mp4"):
            await callback.message.reply_video(f"{file}")
            os.remove(f"{file}")
            break
        else:
            continue

    await msg.delete()


@app.on_message(filters.command("playlist"))
async def download_cmd(_, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: `/playlist <hanime.tv playlist URL only>`")
        return

    url = message.command[1].strip().lower()

    # Detect normal hanime.tv video link and reject it
    if "hanime.tv" in url:
        if "/hentai/video/" in url:
            await message.reply_text("❌ This looks like a *single video link*, not a playlist.\nPlease use a playlist URL containing `playlists`.")
            return
        elif "playlists" not in url:
            await message.reply_text("❌ Invalid URL. Playlist links must contain `playlists`.")
            return
    else:
        await message.reply_text("❌ Please provide a valid hanime.tv playlist URL.")
        return

    chat_id = message.chat.id
    await message.reply_text("Downloading playlist (MP4)... This may take a while ⏳")

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
        await message.reply_text("❌ Download failed or no MP4 file found.")
        return

    for file in mp4_files:
        await asyncio.sleep(0.5)
        await app.send_video(chat_id, file, caption=f"{file}")
        os.remove(file)

    await message.reply_text("✅ All playlist videos sent! 🎉")


# ---------------- RUN ----------------
print("installing yt-dlp first")
subprocess.run(['sudo', 'apt', 'update'])
subprocess.run(['sudo', 'apt', 'install', 'yt-dlp'])
print("yt-dlp installed ")
app.start()
idle()
