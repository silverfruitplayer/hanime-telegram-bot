from pyrogram import *
from pyrogram.types import *

@Client.on_message(filters.command("start"))
async def start(client, message):
   await message.reply_text("""**/search <hentai name> to search**\n Powered By @MetaVoid""")
